import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { workoutQuestsAPI, Quest, UserStats } from "@/lib/api/workout-quests";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Trophy, Dumbbell, Coins, Zap, Target, Gift, CheckCircle, ArrowLeft, LogOut } from "lucide-react";
import { toast } from "sonner";
import { FloatingOrbs } from "@/components/FloatingOrbs";
import { useUserStore } from "@/store/userStore";
import QuestDetailsDialog from "@/components/workout-quests/QuestDetailsDialog";
import StatsCard from "@/components/workout-quests/StatsCard";

/**
 * Workout Quests Page
 * 
 * Maps CLI menu options from main.py to button-based UI:
 * - Menu option "1" (View Active Quests) → Active Quests tab
 * - Menu option "2" (View Quest Details) → "View Details" button
 * - Menu option "3" (Complete a Quest) → "Complete" button  
 * - Menu option "4" (Generate New Workout Plan) → "Generate Plan" button + dropdowns
 * - Menu option "5" (View Profile Summary) → Stats dashboard
 */
export default function WorkoutQuests() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, totalXP, addXP, logout } = useUserStore();
  
  const [userId] = useState(user?.email || "user_1");
  const [fitnessLevel, setFitnessLevel] = useState<string>(
    location.state?.fitnessLevel || "intermediate"
  );
  const [selectedDifficulty] = useState(location.state?.difficulty || "balanced");
  const [stats, setStats] = useState<UserStats | null>(null);
  const [activeQuests, setActiveQuests] = useState<Quest[]>([]);
  const [completedQuests, setCompletedQuests] = useState<Quest[]>([]);
  const [selectedQuest, setSelectedQuest] = useState<Quest | null>(null);
  const [loading, setLoading] = useState(false);
  const [planWeeks, setPlanWeeks] = useState("4");

  // Load data on mount
  useEffect(() => {
    loadUserData();
  }, [userId]);

  const loadUserData = async () => {
    try {
      const [statsData, activeData, completedData] = await Promise.all([
        workoutQuestsAPI.getUserStats(userId),
        workoutQuestsAPI.getActiveQuests(userId),
        workoutQuestsAPI.getCompletedQuests(userId),
      ]);

      setStats(statsData);
      setActiveQuests(activeData);
      setCompletedQuests(completedData);
      
      if (statsData.fitness_level) {
        setFitnessLevel(statsData.fitness_level);
      }
    } catch (error) {
      console.error("Failed to load user data:", error);
      toast.error("Failed to connect to backend", {
        description: "Make sure the API server is running on http://localhost:8000",
      });
    }
  };

  /**
   * Maps to Menu Option 4: Generate New Workout Plan
   * Replaces the interactive prompts with dropdown selections
   */
  const handleGeneratePlan = async () => {
    setLoading(true);
    try {
      // Create/update user with selected fitness level
      await workoutQuestsAPI.createUser(userId, fitnessLevel);

      // Generate workout plan
      const result = await workoutQuestsAPI.generateWorkoutPlan(userId, parseInt(planWeeks));

      toast.success("Workout Plan Generated!", {
        description: `Created ${result.quests_created} workout quests for ${result.duration_weeks} weeks`,
      });

      // Reload data
      await loadUserData();
    } catch (error) {
      toast.error("Failed to generate workout plan");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Maps to Menu Option 3: Complete a Quest
   * Replaces the confirmation prompt with button click
   */
  const handleCompleteQuest = async (questId: string) => {
    try {
      const result = await workoutQuestsAPI.completeQuest(userId, questId);

      // Add XP to main user store
      addXP(result.rewards.xp);

      toast.success("Quest Completed! 🎉", {
        description: `+${result.rewards.xp} XP, +${result.rewards.coins} coins`,
      });

      // Reload data
      await loadUserData();
      setSelectedQuest(null);
    } catch (error) {
      toast.error("Failed to complete quest");
      console.error(error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    toast.success('Logged out successfully');
  };

  return (
    <div className="min-h-screen relative overflow-hidden pb-16">
      <FloatingOrbs />
      
      <div className="container mx-auto px-4 py-8 relative z-10">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="font-heading text-4xl md:text-5xl font-bold text-white flex items-center gap-3">
              <Dumbbell className="h-10 w-10" />
              Fitness Quests
            </h1>
            <p className="text-muted-foreground mt-2 font-body text-lg">
              Complete workout quests to earn XP, coins, and rewards
            </p>
          </div>
          
          <div className="flex gap-3">
            <motion.button
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-gray-700 to-gray-600 text-white font-heading font-semibold shadow-lg"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <ArrowLeft className="w-5 h-5" />
              Dashboard
            </motion.button>
            <motion.button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-destructive to-red-600 text-white font-heading font-semibold shadow-lg"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <LogOut className="w-5 h-5" />
              Logout
            </motion.button>
          </div>
        </div>

      {/* Stats Dashboard - Maps to Menu Option 5: View Profile Summary */}
      {stats && (
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <div className="bg-gradient-to-br from-yellow-600 to-yellow-700 rounded-2xl p-6 shadow-2xl border border-yellow-500/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-yellow-200 text-sm font-body">Total Workouts</p>
                  <p className="text-3xl font-heading font-bold text-white mt-2">{stats.total_workouts}</p>
                </div>
                <Trophy className="h-8 w-8 text-yellow-300 opacity-80" />
              </div>
            </div>
          </motion.div>
          
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <div className="bg-gradient-to-br from-purple-600 to-purple-700 rounded-2xl p-6 shadow-2xl border border-purple-500/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-200 text-sm font-body">Total XP</p>
                  <p className="text-3xl font-heading font-bold text-white mt-2">{totalXP}</p>
                </div>
                <Zap className="h-8 w-8 text-purple-300 opacity-80" />
              </div>
            </div>
          </motion.div>
          
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <div className="bg-gradient-to-br from-amber-600 to-amber-700 rounded-2xl p-6 shadow-2xl border border-amber-500/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-amber-200 text-sm font-body">Total Coins</p>
                  <p className="text-3xl font-heading font-bold text-white mt-2">{stats.total_coins}</p>
                </div>
                <Coins className="h-8 w-8 text-amber-300 opacity-80" />
              </div>
            </div>
          </motion.div>
          
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl p-6 shadow-2xl border border-blue-500/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-200 text-sm font-body">Active Quests</p>
                  <p className="text-3xl font-heading font-bold text-white mt-2">{stats.active_quests}</p>
                </div>
                <Target className="h-8 w-8 text-blue-300 opacity-80" />
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* Generate New Plan - Maps to Menu Option 4 */}
      <motion.div
        className="bg-gradient-to-br from-card/90 to-card/50 backdrop-blur-xl rounded-2xl p-6 shadow-2xl border border-white/10 mb-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <h2 className="font-heading text-2xl font-bold text-white mb-2">Generate New Workout Plan</h2>
        <p className="text-muted-foreground font-body mb-4">
          Fitness Level: <span className="text-white font-semibold capitalize">{fitnessLevel}</span> • 
          Based on your {selectedDifficulty} preference
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 items-end">
          <div className="flex-1">
            <label className="text-sm font-medium text-white mb-2 block">Duration (weeks)</label>
            <Select value={planWeeks} onValueChange={setPlanWeeks}>
              <SelectTrigger className="bg-background/50 border-white/10">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="2">2 weeks</SelectItem>
                <SelectItem value="4">4 weeks</SelectItem>
                <SelectItem value="6">6 weeks</SelectItem>
                <SelectItem value="8">8 weeks</SelectItem>
                <SelectItem value="12">12 weeks</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex-1">
            <motion.button
              onClick={handleGeneratePlan}
              disabled={loading}
              className="w-full py-3 px-6 rounded-xl gradient-bg shine-effect font-heading font-bold text-white shadow-2xl flex items-center justify-center gap-2"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              style={{
                boxShadow: '0 10px 40px -10px hsl(var(--glow-primary)), 0 0 60px -20px hsl(var(--glow-secondary))',
              }}
            >
              <Zap className="w-5 h-5" />
              {loading ? "Generating..." : "Generate Plan"}
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Quests Tabs - Maps to Menu Options 1 & 2 */}
      <Tabs defaultValue="active" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="active">
            Active Quests ({activeQuests.length})
          </TabsTrigger>
          <TabsTrigger value="completed">
            Completed ({completedQuests.length})
          </TabsTrigger>
        </TabsList>

        {/* Active Quests Tab - Menu Option 1 */}
        <TabsContent value="active" className="space-y-4 mt-4">
          {activeQuests.length === 0 ? (
            <motion.div
              className="bg-gradient-to-br from-card/50 to-card/30 backdrop-blur-sm rounded-2xl p-12 text-center border border-white/10"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <Target className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
              <p className="text-xl font-heading font-bold text-white">No active quests</p>
              <p className="text-muted-foreground font-body mt-2">
                Generate a workout plan to get started!
              </p>
            </motion.div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {activeQuests.map((quest, index) => (
                <motion.div
                  key={quest.quest_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <QuestCard
                    quest={quest}
                    onViewDetails={() => setSelectedQuest(quest)}
                    onComplete={() => handleCompleteQuest(quest.quest_id)}
                  />
                </motion.div>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Completed Quests Tab */}
        <TabsContent value="completed" className="space-y-4 mt-4">
          {completedQuests.length === 0 ? (
            <motion.div
              className="bg-gradient-to-br from-card/50 to-card/30 backdrop-blur-sm rounded-2xl p-12 text-center border border-white/10"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <CheckCircle className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
              <p className="text-xl font-heading font-bold text-white">No completed quests yet</p>
              <p className="text-muted-foreground font-body mt-2">
                Complete your first workout to see it here!
              </p>
            </motion.div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {completedQuests.map((quest, index) => (
                <motion.div
                  key={quest.quest_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <QuestCard
                    quest={quest}
                    onViewDetails={() => setSelectedQuest(quest)}
                    completed
                  />
                </motion.div>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Quest Details Dialog - Maps to Menu Option 2 */}
      {selectedQuest && (
        <QuestDetailsDialog
          quest={selectedQuest}
          open={!!selectedQuest}
          onClose={() => setSelectedQuest(null)}
          onComplete={
            selectedQuest.status === "active"
              ? () => handleCompleteQuest(selectedQuest.quest_id)
              : undefined
          }
        />
      )}
      </div>
    </div>
  );
}

/**
 * Quest Card Component
 * Shows quest preview with action buttons
 */
interface QuestCardProps {
  quest: Quest;
  onViewDetails: () => void;
  onComplete?: () => void;
  completed?: boolean;
}

function QuestCard({ quest, onViewDetails, onComplete, completed }: QuestCardProps) {
  return (
    <motion.div
      className={`relative rounded-2xl p-6 backdrop-blur-sm border transition-all ${
        completed 
          ? 'bg-gradient-to-br from-card/30 to-card/20 border-white/5 opacity-75' 
          : 'bg-gradient-to-br from-card/90 to-card/50 border-white/10 hover:border-white/20'
      }`}
      whileHover={!completed ? { scale: 1.02, y: -5 } : {}}
      style={{
        boxShadow: completed 
          ? 'none'
          : '0 10px 40px -10px rgba(0, 0, 0, 0.3)',
      }}
    >
      {/* Status Badge */}
      <div className="absolute top-4 right-4">
        <Badge 
          variant={completed ? "secondary" : "default"}
          className={completed ? "bg-white/10" : "bg-gradient-to-r from-primary to-purple-600"}
        >
          {completed ? "Completed" : "Active"}
        </Badge>
      </div>

      {/* Quest Title */}
      <div className="mb-4 pr-20">
        <h3 className="font-heading text-xl font-bold text-white mb-1">
          {quest.title}
        </h3>
        <p className="text-sm text-muted-foreground font-body">
          {quest.exercises.length} exercises
        </p>
      </div>

      {/* Description */}
      <p className="text-sm text-muted-foreground font-body mb-4 line-clamp-2">
        {quest.description}
      </p>

      {/* Rewards */}
      <div className="flex items-center gap-4 mb-4">
        <div className="flex items-center gap-1.5">
          <div className="p-1.5 rounded-lg bg-purple-500/20">
            <Zap className="h-4 w-4 text-purple-400" />
          </div>
          <span className="font-heading font-semibold text-white">{quest.experience_reward} XP</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="p-1.5 rounded-lg bg-amber-500/20">
            <Coins className="h-4 w-4 text-amber-400" />
          </div>
          <span className="font-heading font-semibold text-white">{quest.coin_reward}</span>
        </div>
        {quest.cached_rewards.length > 0 && (
          <div className="flex items-center gap-1.5">
            <div className="p-1.5 rounded-lg bg-pink-500/20">
              <Gift className="h-4 w-4 text-pink-400" />
            </div>
            <span className="font-heading font-semibold text-white">{quest.cached_rewards.length}</span>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <motion.button
          onClick={onViewDetails}
          className="flex-1 py-2 px-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white font-heading font-semibold transition-colors"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          View Details
        </motion.button>
        {!completed && onComplete && (
          <motion.button
            onClick={onComplete}
            className="flex-1 py-2 px-4 rounded-xl gradient-bg shine-effect text-white font-heading font-semibold"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Complete
          </motion.button>
        )}
      </div>
    </motion.div>
  );
}

