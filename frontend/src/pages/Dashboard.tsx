import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, LogOut, Flame, Target, Zap, Dumbbell, Gift } from 'lucide-react';
import { FloatingOrbs } from '@/components/FloatingOrbs';
import { PlayerCard } from '@/components/PlayerCard';
import { QuestCard } from '@/components/QuestCard';
import { LevelUpModal } from '@/components/LevelUpModal';
import { useUserStore } from '@/store/userStore';
import { generateQuests } from '@/utils/questGenerator';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { workoutQuestsAPI, Quest as WorkoutQuest, UserStats } from '@/lib/api/workout-quests';
import QuestDetailsDialog from '@/components/workout-quests/QuestDetailsDialog';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function Dashboard() {
  const navigate = useNavigate();
  const {
    user,
    preferences,
    quests,
    totalXP,
    level,
    completedCount,
    streak,
    logout,
    addQuests,
    completeQuest,
    addXP,
  } = useUserStore();

  const [showLevelUpModal, setShowLevelUpModal] = useState(false);
  const [newLevel, setNewLevel] = useState(1);
  
  // Workout Quests State
  const [workoutStats, setWorkoutStats] = useState<UserStats | null>(null);
  const [activeWorkoutQuests, setActiveWorkoutQuests] = useState<WorkoutQuest[]>([]);
  const [completedWorkoutQuests, setCompletedWorkoutQuests] = useState<WorkoutQuest[]>([]);
  const [selectedWorkoutQuest, setSelectedWorkoutQuest] = useState<WorkoutQuest | null>(null);
  const [loadingWorkout, setLoadingWorkout] = useState(false);
  const [planWeeks, setPlanWeeks] = useState("4");

  useEffect(() => {
    // If no preferences, redirect to onboarding
    if (!preferences) {
      navigate('/onboarding');
    }
  }, [preferences, navigate]);

  // Load workout quests if fitness is selected
  useEffect(() => {
    if (preferences?.focusAreas.includes('fitness') && user?.email) {
      loadWorkoutData();
    }
  }, [preferences, user]);

  const loadWorkoutData = async () => {
    if (!user?.email) return;
    
    try {
      const [statsData, activeData, completedData] = await Promise.all([
        workoutQuestsAPI.getUserStats(user.email),
        workoutQuestsAPI.getActiveQuests(user.email),
        workoutQuestsAPI.getCompletedQuests(user.email),
      ]);

      setWorkoutStats(statsData);
      setActiveWorkoutQuests(activeData);
      setCompletedWorkoutQuests(completedData);
    } catch (error) {
      console.error("Failed to load workout data:", error);
    }
  };

  const handleGenerateQuests = () => {
    if (!preferences) return;

    const newQuests = generateQuests(
      preferences.focusAreas,
      preferences.difficulty,
      5
    );

    addQuests(newQuests);
    toast.success('New quests generated!');
  };

  const handleCompleteQuest = (questId: string) => {
    const result = completeQuest(questId);

    if (result?.leveledUp) {
      setNewLevel(result.newLevel);
      setShowLevelUpModal(true);
    }

    toast.success('Quest completed! XP earned!');
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    toast.success('Logged out successfully');
  };

  const handleGenerateWorkoutPlan = async () => {
    if (!user?.email || !preferences) return;
    
    setLoadingWorkout(true);
    try {
      const fitnessLevel = preferences.difficulty === 'casual' ? 'beginner' : 
                          preferences.difficulty === 'balanced' ? 'intermediate' : 'expert';
      
      await workoutQuestsAPI.createUser(user.email, fitnessLevel);
      const result = await workoutQuestsAPI.generateWorkoutPlan(user.email, parseInt(planWeeks));

      toast.success("Workout Plan Generated!", {
        description: `Created ${result.quests_created} workout quests for ${result.duration_weeks} weeks`,
      });

      await loadWorkoutData();
    } catch (error) {
      toast.error("Failed to generate workout plan");
      console.error(error);
    } finally {
      setLoadingWorkout(false);
    }
  };

  const handleCompleteWorkoutQuest = async (questId: string) => {
    if (!user?.email) return;
    
    try {
      const result = await workoutQuestsAPI.completeQuest(user.email, questId);
      
      // Store current level before adding XP
      const currentLevel = level;
      
      // Add XP to main user store (this updates level automatically)
      addXP(result.rewards.xp);
      
      // Check if leveled up after a brief delay to ensure state is updated
      setTimeout(() => {
        const newLevelAfterXP = useUserStore.getState().level;
        if (newLevelAfterXP > currentLevel) {
          setNewLevel(newLevelAfterXP);
          setShowLevelUpModal(true);
        }
      }, 100);

      toast.success("Workout Quest Completed! 🎉", {
        description: `+${result.rewards.xp} XP earned!`,
      });

      await loadWorkoutData();
      setSelectedWorkoutQuest(null);
    } catch (error) {
      toast.error("Failed to complete workout quest");
      console.error(error);
    }
  };

  const activeQuests = quests.filter((q) => q.status === 'active');
  const completedQuests = quests.filter((q) => q.status === 'completed');

  if (!user || !preferences) {
    return null;
  }

  const stats = [
    {
      icon: Flame,
      label: 'Streak',
      value: `${streak} days`,
      color: '#F59E0B',
    },
    {
      icon: Target,
      label: 'Completed',
      value: completedCount,
      color: '#3B82F6',
    },
    {
      icon: Zap,
      label: 'Total XP',
      value: totalXP,
      color: '#06B6D4',
    },
  ];

  return (
    <div className="min-h-screen relative overflow-hidden pb-16">
      <FloatingOrbs />

      <div className="container mx-auto px-4 py-8 relative z-10">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="font-heading text-4xl md:text-5xl font-bold text-white">
            Quest Board
          </h1>
          
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

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Player Card */}
            <PlayerCard
              name={user.name}
              picture={user.picture}
              level={level}
              totalXP={totalXP}
            />

            {/* Generate Quests Button */}
            <motion.div
              className="w-full rounded-2xl gradient-bg shine-effect shadow-2xl p-6"
              style={{
                boxShadow: '0 10px 40px -10px hsl(var(--glow-primary)), 0 0 60px -20px hsl(var(--glow-secondary))',
              }}
            >
              <div className="flex flex-col sm:flex-row gap-4 items-end">
                {preferences?.focusAreas.includes('fitness') && (
                  <div className="flex-1">
                    <label className="text-sm font-body font-medium text-white mb-2 block">
                      Workout Plan Duration
                    </label>
                    <Select value={planWeeks} onValueChange={setPlanWeeks}>
                      <SelectTrigger className="bg-white/10 border-white/20 text-white font-body">
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
                )}
                <motion.button
                  onClick={preferences?.focusAreas.includes('fitness') ? handleGenerateWorkoutPlan : handleGenerateQuests}
                  disabled={loadingWorkout}
                  className={`${preferences?.focusAreas.includes('fitness') ? 'flex-1' : 'w-full'} py-5 px-6 rounded-xl font-heading font-bold text-lg text-white flex items-center justify-center gap-3 bg-white/10 hover:bg-white/20 transition-colors`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Plus className="w-6 h-6" />
                  {loadingWorkout ? "Generating..." : "Generate New Quests"}
                </motion.button>
              </div>
            </motion.div>

            {/* Fitness Workout Quests Section */}
            {preferences?.focusAreas.includes('fitness') && (
              <div className="space-y-6">
                {/* Active Workout Quests */}
                {activeWorkoutQuests.length > 0 && (
                  <div>
                    <h3 className="font-heading text-xl font-bold text-white mb-4">
                      Active Workout Quests
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {activeWorkoutQuests.map((quest, index) => (
                        <WorkoutQuestCard
                          key={quest.quest_id}
                          quest={quest}
                          onViewDetails={() => setSelectedWorkoutQuest(quest)}
                          onComplete={() => handleCompleteWorkoutQuest(quest.quest_id)}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Completed Workout Quests */}
                {completedWorkoutQuests.length > 0 && (
                  <div>
                    <h3 className="font-heading text-xl font-bold text-white mb-4">
                      Completed Workout Quests
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {completedWorkoutQuests.map((quest) => (
                        <WorkoutQuestCard
                          key={quest.quest_id}
                          quest={quest}
                          onViewDetails={() => setSelectedWorkoutQuest(quest)}
                          completed
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Active Quests */}
            {activeQuests.length > 0 && (
              <div>
                <h2 className="font-heading text-2xl font-bold text-white mb-4">
                  Active Quests
                </h2>
                <motion.div
                  className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ staggerChildren: 0.1 }}
                >
                  {activeQuests.map((quest, index) => (
                    <motion.div
                      key={quest.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <QuestCard quest={quest} onComplete={handleCompleteQuest} />
                    </motion.div>
                  ))}
                </motion.div>
              </div>
            )}

            {/* Completed Quests */}
            {completedQuests.length > 0 && (
              <div>
                <h2 className="font-heading text-2xl font-bold text-white mb-4">
                  Completed Quests
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {completedQuests.map((quest) => (
                    <QuestCard
                      key={quest.id}
                      quest={quest}
                      onComplete={() => {}}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {activeQuests.length === 0 && completedQuests.length === 0 && (
              <div className="glass rounded-2xl p-12 text-center">
                <h3 className="font-heading text-2xl font-bold text-white mb-2">
                  No Quests Yet
                </h3>
                <p className="text-muted-foreground font-body mb-6">
                  Click the button above to generate your first set of quests!
                </p>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Statistics Card */}
            <div className="glass glass-hover rounded-2xl p-6">
              <h3 className="font-heading text-xl font-bold text-white mb-4">
                Statistics
              </h3>
              <div className="space-y-4">
                {stats.map((stat) => (
                  <div
                    key={stat.label}
                    className="glass rounded-xl p-4 flex items-center gap-4"
                  >
                    <div
                      className="w-12 h-12 rounded-xl flex items-center justify-center"
                      style={{
                        backgroundColor: `${stat.color}40`,
                        boxShadow: `0 5px 20px -5px ${stat.color}60`,
                      }}
                    >
                      <stat.icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <p className="text-muted-foreground text-sm font-body">
                        {stat.label}
                      </p>
                      <p className="font-heading text-2xl font-bold text-white">
                        {stat.value}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Preferences Card */}
            <div className="glass glass-hover rounded-2xl p-6 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-secondary/5 -z-10" />
              
              <h3 className="font-heading text-xl font-bold text-white mb-4">
                Your Path
              </h3>
              
              <div className="space-y-3">
                <div>
                  <p className="text-muted-foreground text-sm font-body mb-2">
                    Focus Areas
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {preferences.focusAreas.map((area) => (
                      <span
                        key={area}
                        className="px-3 py-1 rounded-lg gradient-bg text-white font-body text-sm font-semibold"
                      >
                        {area.charAt(0).toUpperCase() + area.slice(1)}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div>
                  <p className="text-muted-foreground text-sm font-body mb-2">
                    Difficulty
                  </p>
                  <span className="px-3 py-1 rounded-lg gradient-bg text-white font-body text-sm font-semibold inline-block">
                    {preferences.difficulty.charAt(0).toUpperCase() +
                      preferences.difficulty.slice(1)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Level Up Modal */}
      <LevelUpModal
        isOpen={showLevelUpModal}
        level={newLevel}
        onClose={() => setShowLevelUpModal(false)}
      />

      {/* Workout Quest Details Dialog */}
      {selectedWorkoutQuest && (
        <QuestDetailsDialog
          quest={selectedWorkoutQuest}
          open={!!selectedWorkoutQuest}
          onClose={() => setSelectedWorkoutQuest(null)}
          onComplete={
            selectedWorkoutQuest.status === "active"
              ? () => handleCompleteWorkoutQuest(selectedWorkoutQuest.quest_id)
              : undefined
          }
        />
      )}
    </div>
  );
}

// Workout Quest Card Component
interface WorkoutQuestCardProps {
  quest: WorkoutQuest;
  onViewDetails: () => void;
  onComplete?: () => void;
  completed?: boolean;
}

function WorkoutQuestCard({ quest, onViewDetails, onComplete, completed }: WorkoutQuestCardProps) {
  return (
    <motion.div
      className={`relative rounded-2xl p-5 backdrop-blur-sm border transition-all ${
        completed 
          ? 'bg-gradient-to-br from-card/30 to-card/20 border-white/5 opacity-75' 
          : 'bg-gradient-to-br from-card/90 to-card/50 border-white/10 hover:border-white/20'
      }`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={!completed ? { scale: 1.02, y: -5 } : {}}
      style={{
        boxShadow: completed 
          ? 'none'
          : '0 10px 40px -10px rgba(0, 0, 0, 0.3)',
      }}
    >
      {/* Status Badge */}
      <div className="absolute top-3 right-3">
        <Badge 
          variant={completed ? "secondary" : "default"}
          className={completed ? "bg-white/10 text-xs" : "bg-gradient-to-r from-primary to-purple-600 text-xs"}
        >
          {completed ? "Completed" : "Active"}
        </Badge>
      </div>

      {/* Quest Title */}
      <div className="mb-3 pr-20">
        <h3 className="font-heading text-lg font-bold text-white mb-1">
          {quest.title}
        </h3>
        <p className="text-xs text-muted-foreground font-body">
          {quest.exercises.length} exercises
        </p>
      </div>

      {/* Description */}
      <p className="text-xs text-muted-foreground font-body mb-3 line-clamp-2">
        {quest.description}
      </p>

      {/* Rewards */}
      <div className="flex items-center gap-3 mb-3">
        <div className="flex items-center gap-1.5">
          <div className="p-1.5 rounded-lg bg-purple-500/20">
            <Zap className="h-4 w-4 text-purple-400" />
          </div>
          <span className="font-heading font-semibold text-white">
            {quest.experience_reward} XP
          </span>
        </div>
        {quest.cached_rewards.length > 0 && (
          <div className="flex items-center gap-1.5">
            <div className="p-1.5 rounded-lg bg-pink-500/20">
              <Gift className="h-4 w-4 text-pink-400" />
            </div>
            <span className="font-heading font-semibold text-white">
              {quest.cached_rewards.length} Reward{quest.cached_rewards.length !== 1 ? 's' : ''}
            </span>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <motion.button
          onClick={onViewDetails}
          className="flex-1 py-2 px-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white font-heading font-semibold text-sm transition-colors"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          View Details
        </motion.button>
        {!completed && onComplete && (
          <motion.button
            onClick={onComplete}
            className="flex-1 py-2 px-3 rounded-xl gradient-bg shine-effect text-white font-heading font-semibold text-sm"
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
