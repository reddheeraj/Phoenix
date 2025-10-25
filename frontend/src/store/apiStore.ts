import { create } from 'zustand';
import { apiService } from '@/services/api';
import {
  ApiQuest,
  ApiUserStats,
  ApiUserPreferences,
  QuestCompletionResponse,
  OnboardingRequest,
  OnboardingResponse,
  UserProfile,
} from '@/types/quest';
import { toast } from 'sonner';

interface ApiStore {
  // State
  user: UserProfile | null;
  userStats: ApiUserStats | null;
  userPreferences: ApiUserPreferences | null;
  quests: ApiQuest[];
  isLoading: boolean;
  error: string | null;

  // Actions
  setUser: (user: UserProfile) => void;
  clearUser: () => void;
  
  // Onboarding
  completeOnboarding: (data: OnboardingRequest) => Promise<OnboardingResponse | null>;
  
  // User data
  fetchUserStats: (userId: string) => Promise<void>;
  fetchUserPreferences: (userId: string) => Promise<void>;
  updateUserPreferences: (userId: string, preferences: Partial<ApiUserPreferences>) => Promise<void>;
  
  // Quests
  fetchUserQuests: (userId: string, questType?: 'daily_task' | 'email_based') => Promise<void>;
  completeQuest: (userId: string, questId: number) => Promise<QuestCompletionResponse | null>;
  
  // Email processing
  processUserEmails: (userId: string, days?: number) => Promise<void>;
  
  // Utility
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

export const useApiStore = create<ApiStore>((set, get) => ({
  // Initial state
  user: null,
  userStats: null,
  userPreferences: null,
  quests: [],
  isLoading: false,
  error: null,

  // Set user
  setUser: (user) => {
    set({ user });
  },

  // Clear user
  clearUser: () => {
    set({
      user: null,
      userStats: null,
      userPreferences: null,
      quests: [],
      error: null,
    });
  },

  // Complete onboarding
  completeOnboarding: async (data) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await apiService.completeOnboarding(
        data.user_id,
        data.daily_tasks,
        data.long_term_goals
      );

      if (response.error) {
        set({ error: response.error, isLoading: false });
        toast.error(`Onboarding failed: ${response.error}`);
        return null;
      }

      set({ isLoading: false });
      toast.success('Onboarding completed successfully!');
      return response.data!;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      set({ error: errorMessage, isLoading: false });
      toast.error(`Onboarding failed: ${errorMessage}`);
      return null;
    }
  },

  // Fetch user stats
  fetchUserStats: async (userId) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await apiService.getUserStats(userId);

      if (response.error) {
        set({ error: response.error, isLoading: false });
        return;
      }

      set({ userStats: response.data!, isLoading: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      set({ error: errorMessage, isLoading: false });
    }
  },

  // Fetch user preferences
  fetchUserPreferences: async (userId) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await apiService.getUserPreferences(userId);

      if (response.error) {
        set({ error: response.error, isLoading: false });
        return;
      }

      set({ userPreferences: response.data!, isLoading: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      set({ error: errorMessage, isLoading: false });
    }
  },

  // Update user preferences
  updateUserPreferences: async (userId, preferences) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await apiService.updateUserPreferences(userId, preferences);

      if (response.error) {
        set({ error: response.error, isLoading: false });
        toast.error(`Failed to update preferences: ${response.error}`);
        return;
      }

      // Refresh preferences after update
      await get().fetchUserPreferences(userId);
      set({ isLoading: false });
      toast.success('Preferences updated successfully!');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      set({ error: errorMessage, isLoading: false });
      toast.error(`Failed to update preferences: ${errorMessage}`);
    }
  },

  // Fetch user quests
  fetchUserQuests: async (userId, questType) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await apiService.getUserQuests(userId, questType);

      if (response.error) {
        set({ error: response.error, isLoading: false });
        return;
      }

      set({ quests: response.data!, isLoading: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      set({ error: errorMessage, isLoading: false });
    }
  },

  // Complete quest
  completeQuest: async (userId, questId) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await apiService.completeQuest(userId, questId);

      if (response.error) {
        set({ error: response.error, isLoading: false });
        toast.error(`Failed to complete quest: ${response.error}`);
        return null;
      }

      const result = response.data!;
      
      // Update quests list
      const { quests } = get();
      const updatedQuests = quests.map(quest =>
        quest.id === questId
          ? { ...quest, status: 'completed' as const }
          : quest
      );
      set({ quests: updatedQuests, isLoading: false });

      // Show celebration message
      toast.success(result.message);

      // Refresh user stats
      await get().fetchUserStats(userId);

      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      set({ error: errorMessage, isLoading: false });
      toast.error(`Failed to complete quest: ${errorMessage}`);
      return null;
    }
  },

  // Process user emails
  processUserEmails: async (userId, days = 7) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await apiService.processUserEmails(userId, days);

      if (response.error) {
        set({ error: response.error, isLoading: false });
        toast.error(`Failed to process emails: ${response.error}`);
        return;
      }

      const result = response.data!;
      set({ isLoading: false });
      
      toast.success(
        `Email processing completed! Processed ${result.emails_processed} emails and created ${result.quests_created} quests.`
      );

      // Refresh quests and stats
      await Promise.all([
        get().fetchUserQuests(userId),
        get().fetchUserStats(userId),
      ]);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      set({ error: errorMessage, isLoading: false });
      toast.error(`Failed to process emails: ${errorMessage}`);
    }
  },

  // Utility functions
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
}));
