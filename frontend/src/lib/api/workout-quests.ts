/**
 * API client for Workout Quests backend
 * Mirrors the functionality from main.py WorkoutQuestSystem class
 */

const API_BASE_URL = "http://localhost:8000/api";

export interface Exercise {
  name: string;
  sets: number;
  reps: number;
  rest_seconds: number;
  muscle: string;
  equipment: string;
  difficulty: string;
  instructions: string;
}

export interface Quest {
  quest_id: string;
  title: string;
  description: string;
  status: string;
  experience_reward: number;
  coin_reward: number;
  exercises: Exercise[];
  cached_rewards: Array<{
    merchant?: string;
    store?: string;
    offer?: string;
    discount?: string;
  }>;
  created_at: string;
}

export interface UserStats {
  user_id: string;
  fitness_level: string;
  total_workouts: number;
  total_xp: number;
  total_coins: number;
  active_quests: number;
  completed_quests: number;
  current_plan_days: number;
}

export interface UserProfile {
  user_id: string;
  fitness_level: string;
  total_workouts_completed: number;
  total_experience_earned: number;
  total_coins_earned: number;
  active_quests_count: number;
  completed_quests_count: number;
}

export class WorkoutQuestsAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Create user profile
   * Maps to: create_user_profile() in main.py
   */
  async createUser(userId: string, fitnessLevel: string): Promise<UserProfile> {
    const response = await fetch(`${this.baseUrl}/users`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, fitness_level: fitnessLevel }),
    });

    if (!response.ok) {
      throw new Error("Failed to create user");
    }

    return response.json();
  }

  /**
   * Get user profile
   * Maps to: get_profile_summary() in main.py
   */
  async getUserProfile(userId: string): Promise<UserProfile> {
    const response = await fetch(`${this.baseUrl}/users/${userId}`);

    if (!response.ok) {
      throw new Error("Failed to fetch user profile");
    }

    return response.json();
  }

  /**
   * Get user statistics
   */
  async getUserStats(userId: string): Promise<UserStats> {
    const response = await fetch(`${this.baseUrl}/users/${userId}/stats`);

    if (!response.ok) {
      throw new Error("Failed to fetch user stats");
    }

    return response.json();
  }

  /**
   * Generate workout plan and create quests
   * Maps to: generate_workout_plan_with_quests() in main.py
   */
  async generateWorkoutPlan(
    userId: string,
    durationWeeks: number = 4
  ): Promise<{
    message: string;
    plan_id: string;
    duration_weeks: number;
    days_per_week: number;
    total_exercises: number;
    quests_created: number;
  }> {
    const response = await fetch(`${this.baseUrl}/users/${userId}/workout-plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ duration_weeks: durationWeeks }),
    });

    if (!response.ok) {
      throw new Error("Failed to generate workout plan");
    }

    return response.json();
  }

  /**
   * Get active quests
   * Maps to: display_active_quests() in main.py
   */
  async getActiveQuests(userId: string): Promise<Quest[]> {
    const response = await fetch(`${this.baseUrl}/users/${userId}/quests`);

    if (!response.ok) {
      throw new Error("Failed to fetch active quests");
    }

    return response.json();
  }

  /**
   * Get quest details
   * Maps to: show_quest_details() in main.py
   */
  async getQuestDetails(userId: string, questId: string): Promise<Quest> {
    const response = await fetch(`${this.baseUrl}/users/${userId}/quests/${questId}`);

    if (!response.ok) {
      throw new Error("Failed to fetch quest details");
    }

    return response.json();
  }

  /**
   * Complete a quest
   * Maps to: complete_quest_interactive() in main.py
   */
  async completeQuest(
    userId: string,
    questId: string
  ): Promise<{
    message: string;
    quest_id: string;
    rewards: {
      xp: number;
      coins: number;
      special_rewards: any[];
    };
    new_stats: {
      total_workouts: number;
      total_xp: number;
      total_coins: number;
    };
  }> {
    const response = await fetch(`${this.baseUrl}/users/${userId}/quests/${questId}/complete`, {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error("Failed to complete quest");
    }

    return response.json();
  }

  /**
   * Get completed quests
   */
  async getCompletedQuests(userId: string): Promise<Quest[]> {
    const response = await fetch(`${this.baseUrl}/users/${userId}/completed-quests`);

    if (!response.ok) {
      throw new Error("Failed to fetch completed quests");
    }

    return response.json();
  }
}

export const workoutQuestsAPI = new WorkoutQuestsAPI();

