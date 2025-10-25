import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, LogOut, Flame, Target, Zap, Mail, RefreshCw } from 'lucide-react';
import { FloatingOrbs } from '@/components/FloatingOrbs';
import { PlayerCard } from '@/components/PlayerCard';
import { QuestCard } from '@/components/QuestCard';
import { LevelUpModal } from '@/components/LevelUpModal';
import { useUserStore } from '@/store/userStore';
import { useApiStore } from '@/store/apiStore';
import { generateQuests } from '@/utils/questGenerator';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

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
  } = useUserStore();

  const {
    user: apiUser,
    userStats,
    userPreferences,
    quests: apiQuests,
    isLoading,
    fetchUserStats,
    fetchUserPreferences,
    fetchUserQuests,
    completeQuest: apiCompleteQuest,
    processUserEmails,
  } = useApiStore();

  const [showLevelUpModal, setShowLevelUpModal] = useState(false);
  const [newLevel, setNewLevel] = useState(1);
  const [questFilter, setQuestFilter] = useState<'all' | 'daily_task' | 'email_based'>('all');

  useEffect(() => {
    // If no preferences, redirect to onboarding
    if (!preferences) {
      navigate('/onboarding');
    }
  }, [preferences, navigate]);

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
            <motion.button
              onClick={handleGenerateQuests}
              className="w-full py-5 rounded-2xl gradient-bg shine-effect font-heading font-bold text-lg text-white shadow-2xl flex items-center justify-center gap-3"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              style={{
                boxShadow: '0 10px 40px -10px hsl(var(--glow-primary)), 0 0 60px -20px hsl(var(--glow-secondary))',
              }}
            >
              <Plus className="w-6 h-6" />
              Generate New Quests
            </motion.button>

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
    </div>
  );
}
