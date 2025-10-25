// API service for Phoenix Solo Leveling System
// Based on OpenAPI specification

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          error: errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  // Health check
  async healthCheck() {
    return this.request<{ status: string; timestamp: string }>('/health');
  }

  // User onboarding
  async completeOnboarding(userId: string, dailyTasks: string[], longTermGoals: string[]) {
    return this.request<{
      message: string;
      user_id: string;
      daily_quests_created: number;
      next_step: string;
    }>('/onboarding', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        daily_tasks: dailyTasks,
        long_term_goals: longTermGoals,
      }),
    });
  }

  // User preferences
  async getUserPreferences(userId: string) {
    return this.request<{
      user_id: string;
      daily_tasks: string[];
      long_term_goals: string[];
    }>(`/users/${userId}/preferences`);
  }

  async updateUserPreferences(
    userId: string,
    preferences: {
      daily_tasks?: string[];
      long_term_goals?: string[];
    }
  ) {
    return this.request<{
      message: string;
      user_id: string;
    }>(`/users/${userId}/preferences`, {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  }

  // User quests
  async getUserQuests(userId: string, questType?: 'daily_task' | 'email_based') {
    const params = questType ? `?quest_type=${questType}` : '';
    return this.request<Array<{
      id: number;
      email_id?: number;
      title: string;
      description: string;
      quest_type: 'daily_task' | 'email_based';
      quest_category: string;
      importance: 'daily' | 'weekly' | 'main_quest' | 'side_quest';
      urgency: 'low' | 'medium' | 'high' | 'critical';
      deadline?: string;
      event_duration_minutes: number;
      calendar_event_id?: string;
      status: 'pending' | 'in_progress' | 'completed';
      created_at: string;
    }>>(`/users/${userId}/quests${params}`);
  }

  // Quest completion with gamification
  async completeQuest(userId: string, questId: number) {
    return this.request<{
      quest_id: number;
      xp_reward: number;
      new_level: number;
      level_ups: number;
      new_total_xp: number;
      new_current_xp: number;
      streak_days: number;
      message: string;
    }>(`/users/${userId}/quests/${questId}/complete`, {
      method: 'POST',
    });
  }

  // User stats
  async getUserStats(userId: string) {
    return this.request<{
      user_id: string;
      level: number;
      total_xp: number;
      current_xp: number;
      quests_completed: number;
      daily_quests_completed: number;
      email_quests_completed: number;
      streak_days: number;
      last_activity_date?: string;
    }>(`/users/${userId}/stats`);
  }

  // Process emails
  async processUserEmails(userId: string, days: number = 7) {
    return this.request<{
      message: string;
      user_id: string;
      emails_processed: number;
      quests_created: number;
      daily_quests_created: number;
    }>(`/users/${userId}/process-emails?days=${days}`, {
      method: 'POST',
    });
  }

  // Leaderboard
  async getLeaderboard(userId: string, limit: number = 10) {
    return this.request<Array<{
      user_id: string;
      level: number;
      total_xp: number;
      quests_completed: number;
      streak_days: number;
    }>>(`/users/${userId}/leaderboard?limit=${limit}`);
  }

  // Quest management (for admin/debugging)
  async getAllQuests(filters?: {
    status?: 'pending' | 'in_progress' | 'completed';
    importance?: 'daily' | 'weekly' | 'main_quest' | 'side_quest';
    urgency?: 'low' | 'medium' | 'high' | 'critical';
  }) {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.importance) params.append('importance', filters.importance);
    if (filters?.urgency) params.append('urgency', filters.urgency);

    const queryString = params.toString();
    return this.request<Array<{
      id: number;
      email_id?: number;
      title: string;
      description: string;
      quest_type: 'daily_task' | 'email_based';
      quest_category: string;
      importance: 'daily' | 'weekly' | 'main_quest' | 'side_quest';
      urgency: 'low' | 'medium' | 'high' | 'critical';
      deadline?: string;
      event_duration_minutes: number;
      calendar_event_id?: string;
      status: 'pending' | 'in_progress' | 'completed';
      created_at: string;
    }>>(`/quests${queryString ? `?${queryString}` : ''}`);
  }

  async getQuest(questId: number) {
    return this.request<{
      id: number;
      email_id?: number;
      title: string;
      description: string;
      quest_type: 'daily_task' | 'email_based';
      quest_category: string;
      importance: 'daily' | 'weekly' | 'main_quest' | 'side_quest';
      urgency: 'low' | 'medium' | 'high' | 'critical';
      deadline?: string;
      event_duration_minutes: number;
      calendar_event_id?: string;
      status: 'pending' | 'in_progress' | 'completed';
      created_at: string;
    }>(`/quests/${questId}`);
  }

  async updateQuest(questId: number, updates: {
    status?: 'pending' | 'in_progress' | 'completed';
    calendar_event_id?: string;
  }) {
    return this.request<{
      id: number;
      email_id?: number;
      title: string;
      description: string;
      quest_type: 'daily_task' | 'email_based';
      quest_category: string;
      importance: 'daily' | 'weekly' | 'main_quest' | 'side_quest';
      urgency: 'low' | 'medium' | 'high' | 'critical';
      deadline?: string;
      event_duration_minutes: number;
      calendar_event_id?: string;
      status: 'pending' | 'in_progress' | 'completed';
      created_at: string;
    }>(`/quests/${questId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  // Email processing (global)
  async processEmails(days: number = 7) {
    return this.request<{
      emails_processed: number;
      quests_created: number;
      calendar_events_created: number;
    }>(`/process-emails?days=${days}`, {
      method: 'POST',
    });
  }

  // Chat with agent
  async chatWithAgent(message: string) {
    return this.request<{
      response: string;
    }>('/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }
}

export const apiService = new ApiService();
export default apiService;
