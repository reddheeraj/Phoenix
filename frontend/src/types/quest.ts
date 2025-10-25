export type QuestRank = 'E' | 'D' | 'C' | 'B' | 'A' | 'S';
export type FocusArea = 'study' | 'fitness' | 'productivity';
export type Difficulty = 'casual' | 'balanced' | 'hardcore';
export type QuestStatus = 'active' | 'completed';

export interface Quest {
  id: string;
  title: string;
  description: string;
  rank: QuestRank;
  xp: number;
  status: QuestStatus;
  focusArea: FocusArea;
  difficulty: Difficulty;
  createdAt: Date;
  completedAt?: Date;
}

export interface UserPreferences {
  focusAreas: FocusArea[];
  difficulty: Difficulty;
}

export interface UserProfile {
  name: string;
  email: string;
  picture: string;
}

export interface UserProgress {
  totalXP: number;
  level: number;
  completedCount: number;
  streak: number;
}
