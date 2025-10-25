// Legacy types for backward compatibility
export type QuestRank = 'E' | 'D' | 'C' | 'B' | 'A' | 'S';
export type FocusArea = 'study' | 'fitness' | 'productivity';
export type Difficulty = 'casual' | 'balanced' | 'hardcore';

// New API-aligned types
export type QuestType = 'daily_task' | 'email_based';
export type QuestCategory = 'daily' | 'work' | 'personal' | 'education' | 'health' | 'general';
export type QuestImportance = 'daily' | 'weekly' | 'main_quest' | 'side_quest';
export type QuestUrgency = 'low' | 'medium' | 'high' | 'critical';
export type QuestStatus = 'pending' | 'completed';

// API Quest interface (matches backend)
export interface ApiQuest {
  id: number;
  email_id?: number;
  title: string;
  description: string;
  quest_type: QuestType;
  quest_category: QuestCategory;
  importance: QuestImportance;
  urgency: QuestUrgency;
  deadline?: string;
  event_duration_minutes: number;
  calendar_event_id?: string;
  status: QuestStatus;
  created_at: string;
}

// Legacy Quest interface (for backward compatibility)
export interface Quest {
  id: string;
  title: string;
  description: string;
  rank: QuestRank;
  xp: number; // Using xp internally but displayed as AP
  status: QuestStatus;
  focusArea: FocusArea;
  difficulty: Difficulty;
  createdAt: Date;
  completedAt?: Date;
}

// API User Preferences (matches backend)
export interface ApiUserPreferences {
  user_id: string;
  daily_tasks: string[];
  long_term_goals: string[];
}

// Legacy User Preferences (for backward compatibility)
export interface UserPreferences {
  focusAreas: FocusArea[];
  difficulty: Difficulty;
}

export interface UserProfile {
  name: string;
  email: string;
  picture: string;
}

// API User Stats (matches backend)
export interface ApiUserStats {
  user_id: string;
  level: number;
  total_xp: number;
  current_xp: number;
  quests_completed: number;
  daily_quests_completed: number;
  email_quests_completed: number;
  streak_days: number;
  last_activity_date?: string;
}

// Legacy User Progress (for backward compatibility)
export interface UserProgress {
  totalXP: number;
  level: number;
  completedCount: number;
  streak: number;
}

// Quest completion response
export interface QuestCompletionResponse {
  quest_id: number;
  xp_reward: number;
  new_level: number;
  level_ups: number;
  new_total_xp: number;
  new_current_xp: number;
  streak_days: number;
  message: string;
}

// Onboarding request
export interface OnboardingRequest {
  user_id: string;
  daily_tasks: string[];
  long_term_goals: string[];
}

// Onboarding response
export interface OnboardingResponse {
  message: string;
  user_id: string;
  daily_quests_created: number;
  next_step: string;
}
