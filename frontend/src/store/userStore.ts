import { create } from 'zustand';
import { Quest, UserPreferences, UserProfile, UserProgress } from '@/types/quest';
import { calculateLevel } from '@/utils/questGenerator';

interface UserStore extends UserProgress {
  // User data
  user: UserProfile | null;
  token: string | null;
  preferences: UserPreferences | null;
  quests: Quest[];
  isInitialized: boolean;

  // Actions
  initializeFromStorage: () => void;
  setUser: (user: UserProfile, token: string) => void;
  logout: () => void;
  setPreferences: (preferences: UserPreferences) => void;
  addQuests: (quests: Quest[]) => void;
  completeQuest: (questId: string) => { leveledUp: boolean; newLevel: number } | undefined;
  addXP: (amount: number) => void;
  updateStreak: () => void;
}

const STORAGE_KEYS = {
  USER: 'quest_user',
  TOKEN: 'quest_token',
  PREFERENCES: 'quest_preferences',
  QUESTS: (userId: string) => `quests_${userId}`,
  PROGRESS: (userId: string) => `quest_progress_${userId}`,
  LAST_ACTIVE: (userId: string) => `last_active_${userId}`,
};

export const useUserStore = create<UserStore>((set, get) => ({
  // Initial state
  user: null,
  token: null,
  preferences: null,
  quests: [],
  totalXP: 0,
  level: 1,
  completedCount: 0,
  streak: 0,
  isInitialized: false,

  // Initialize from localStorage
  initializeFromStorage: () => {
    try {
      const userStr = localStorage.getItem(STORAGE_KEYS.USER);
      const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
      const preferencesStr = localStorage.getItem(STORAGE_KEYS.PREFERENCES);

      if (userStr && token) {
        const user = JSON.parse(userStr);
        const preferences = preferencesStr ? JSON.parse(preferencesStr) : null;

        // Load quests
        const questsStr = localStorage.getItem(STORAGE_KEYS.QUESTS(user.email));
        const quests = questsStr ? JSON.parse(questsStr) : [];

        // Load progress
        const progressStr = localStorage.getItem(STORAGE_KEYS.PROGRESS(user.email));
        const progress = progressStr
          ? JSON.parse(progressStr)
          : { totalXP: 0, level: 1, completedCount: 0, streak: 0 };

        set({
          user,
          token,
          preferences,
          quests,
          ...progress,
          isInitialized: true,
        });
      } else {
        set({ isInitialized: true });
      }
    } catch (error) {
      console.error('Failed to initialize from storage:', error);
      set({ isInitialized: true });
    }
  },

  // Set user and token
  setUser: (user, token) => {
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
    localStorage.setItem(STORAGE_KEYS.TOKEN, token);
    set({ user, token });
  },

  // Logout
  logout: () => {
    const { user } = get();
    if (user) {
      // Clear user-specific data
      localStorage.removeItem(STORAGE_KEYS.QUESTS(user.email));
      localStorage.removeItem(STORAGE_KEYS.PROGRESS(user.email));
      localStorage.removeItem(STORAGE_KEYS.LAST_ACTIVE(user.email));
    }
    // Clear global data
    localStorage.removeItem(STORAGE_KEYS.USER);
    localStorage.removeItem(STORAGE_KEYS.TOKEN);
    localStorage.removeItem(STORAGE_KEYS.PREFERENCES);

    set({
      user: null,
      token: null,
      preferences: null,
      quests: [],
      totalXP: 0,
      level: 1,
      completedCount: 0,
      streak: 0,
    });
  },

  // Set preferences
  setPreferences: (preferences) => {
    localStorage.setItem(STORAGE_KEYS.PREFERENCES, JSON.stringify(preferences));
    set({ preferences });
  },

  // Add quests
  addQuests: (newQuests) => {
    const { user, quests } = get();
    if (!user) return;

    const updatedQuests = [...quests, ...newQuests];
    localStorage.setItem(
      STORAGE_KEYS.QUESTS(user.email),
      JSON.stringify(updatedQuests)
    );
    set({ quests: updatedQuests });
  },

  // Complete quest
  completeQuest: (questId) => {
    const { user, quests, totalXP, completedCount } = get();
    if (!user) return undefined;

    const quest = quests.find((q) => q.id === questId);
    if (!quest || quest.status === 'completed') return undefined;

    // Mark quest as completed
    const updatedQuests = quests.map((q) =>
      q.id === questId
        ? { ...q, status: 'completed' as const, completedAt: new Date() }
        : q
    );

    // Add XP
    const newTotalXP = totalXP + quest.xp;
    const newLevel = calculateLevel(newTotalXP);
    const oldLevel = calculateLevel(totalXP);
    const leveledUp = newLevel > oldLevel;

    // Update completed count
    const newCompletedCount = completedCount + 1;

    // Save to localStorage
    localStorage.setItem(
      STORAGE_KEYS.QUESTS(user.email),
      JSON.stringify(updatedQuests)
    );

    const progress = {
      totalXP: newTotalXP,
      level: newLevel,
      completedCount: newCompletedCount,
      streak: get().streak,
    };

    localStorage.setItem(STORAGE_KEYS.PROGRESS(user.email), JSON.stringify(progress));

    set({
      quests: updatedQuests,
      totalXP: newTotalXP,
      level: newLevel,
      completedCount: newCompletedCount,
    });

    // Update streak
    get().updateStreak();

    return { leveledUp, newLevel };
  },

  // Add XP (for future use)
  addXP: (amount) => {
    const { user, totalXP } = get();
    if (!user) return;

    const newTotalXP = totalXP + amount;
    const newLevel = calculateLevel(newTotalXP);

    const progress = {
      totalXP: newTotalXP,
      level: newLevel,
      completedCount: get().completedCount,
      streak: get().streak,
    };

    localStorage.setItem(STORAGE_KEYS.PROGRESS(user.email), JSON.stringify(progress));

    set({ totalXP: newTotalXP, level: newLevel });
  },

  // Update streak
  updateStreak: () => {
    const { user } = get();
    if (!user) return;

    const lastActiveStr = localStorage.getItem(STORAGE_KEYS.LAST_ACTIVE(user.email));
    const today = new Date().toDateString();

    if (lastActiveStr) {
      const lastActive = new Date(lastActiveStr);
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);

      if (lastActive.toDateString() === yesterday.toDateString()) {
        // Consecutive day - increment streak
        set((state) => {
          const newStreak = state.streak + 1;
          const progress = {
            totalXP: state.totalXP,
            level: state.level,
            completedCount: state.completedCount,
            streak: newStreak,
          };
          localStorage.setItem(
            STORAGE_KEYS.PROGRESS(user.email),
            JSON.stringify(progress)
          );
          return { streak: newStreak };
        });
      } else if (lastActive.toDateString() !== today) {
        // Streak broken
        set((state) => {
          const progress = {
            totalXP: state.totalXP,
            level: state.level,
            completedCount: state.completedCount,
            streak: 1,
          };
          localStorage.setItem(
            STORAGE_KEYS.PROGRESS(user.email),
            JSON.stringify(progress)
          );
          return { streak: 1 };
        });
      }
    } else {
      // First time - start streak
      set({ streak: 1 });
    }

    localStorage.setItem(STORAGE_KEYS.LAST_ACTIVE(user.email), today);
  },
}));
