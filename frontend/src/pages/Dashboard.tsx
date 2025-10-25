import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { LogOut, Flame, Target, Zap, Mail, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import { FloatingOrbs } from '@/components/FloatingOrbs';
import { PlayerCard } from '@/components/PlayerCard';
import { QuestCard } from '@/components/QuestCard';
import { LevelUpModal } from '@/components/LevelUpModal';
import { QuestChat } from '@/components/QuestChat';
import { useUserStore } from '@/store/userStore';
import { useApiStore } from '@/store/apiStore';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const navigate = useNavigate();
  const {
    user,
    preferences,
    logout,
  } = useUserStore();

  const {
    userStats,
    userPreferences,
    quests: apiQuests,
    isLoading,
    checkUserExists,
    fetchUserStats,
    fetchUserPreferences,
    fetchUserQuests,
    completeQuest: apiCompleteQuest,
    processUserEmails,
  } = useApiStore();

  const [showLevelUpModal, setShowLevelUpModal] = useState(false);
  const [newLevel, setNewLevel] = useState(1);
  const [questFilter, setQuestFilter] = useState<'all' | 'daily_task' | 'email_based'>('all');
  const [currentActiveSlide, setCurrentActiveSlide] = useState(0);
  const [currentCompletedSlide, setCurrentCompletedSlide] = useState(0);
  const activeScrollRef = useRef<HTMLDivElement>(null);
  const completedScrollRef = useRef<HTMLDivElement>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize user data on mount
  useEffect(() => {
    if (!user) {
      navigate('/');
      return;
    }

      const initializeData = async () => {
        try {
          // Check if user exists in backend
          const userExists = await checkUserExists(user.email);
          if (!userExists) {
            // User doesn't exist in backend, redirect to onboarding
            navigate('/onboarding');
            return;
          }
          
          // Fetch user preferences
          await fetchUserPreferences(user.email);
          
          // Fetch user stats
          await fetchUserStats(user.email);
          
          // Fetch user quests
          await fetchUserQuests(user.email);
          
          setIsInitialized(true);
        } catch (error) {
          console.error('Failed to initialize user data:', error);
          toast.error('Failed to load your data');
          // On error, redirect to onboarding
          navigate('/onboarding');
        }
      };

    if (!isInitialized) {
      initializeData();
    }
  }, [user, navigate, isInitialized, checkUserExists, fetchUserPreferences, fetchUserStats, fetchUserQuests]);

  const handleSyncEmails = async () => {
    if (!user) return;
    
    setIsSyncing(true);
    try {
      await processUserEmails(user.email, 7); // Process last 7 days
      toast.success('Emails synced successfully! New quests may have been created.');
      
      // Refresh quests after syncing
      await fetchUserQuests(user.email);
    } catch (error) {
      console.error('Failed to sync emails:', error);
      toast.error('Failed to sync emails');
    } finally {
      setIsSyncing(false);
    }
  };

  const handleCompleteQuest = async (questId: string) => {
    if (!user) return;
    
    try {
      const result = await apiCompleteQuest(user.email, parseInt(questId));
      
      if (result) {
        // Check for level ups
        if (result.level_ups > 0) {
          setNewLevel(result.new_level);
          setShowLevelUpModal(true);
        }
        
        toast.success(`Quest completed! +${result.xp_reward} XP earned!`);
        
        // Refresh user stats and quests
        await fetchUserStats(user.email);
        await fetchUserQuests(user.email);
      }
    } catch (error) {
      console.error('Failed to complete quest:', error);
      toast.error('Failed to complete quest');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    toast.success('Logged out successfully');
  };

  // Scroll functions for quest navigation
  const scrollToSlide = (ref: React.RefObject<HTMLDivElement>, slideIndex: number, setSlide: (index: number) => void) => {
    if (ref.current) {
      const slideWidth = ref.current.children[0]?.clientWidth || 0;
      const scrollLeft = slideIndex * (slideWidth + 24); // 24px gap
      ref.current.scrollTo({ left: scrollLeft, behavior: 'smooth' });
      setSlide(slideIndex);
    }
  };

  const scrollActiveQuests = (direction: 'left' | 'right') => {
    const maxSlides = Math.ceil(activeQuests.length / 6);
    const newSlide = direction === 'left' 
      ? Math.max(0, currentActiveSlide - 1)
      : Math.min(maxSlides - 1, currentActiveSlide + 1);
    scrollToSlide(activeScrollRef, newSlide, setCurrentActiveSlide);
  };

  const scrollCompletedQuests = (direction: 'left' | 'right') => {
    const maxSlides = Math.ceil(completedQuests.length / 6);
    const newSlide = direction === 'left' 
      ? Math.max(0, currentCompletedSlide - 1)
      : Math.min(maxSlides - 1, currentCompletedSlide + 1);
    scrollToSlide(completedScrollRef, newSlide, setCurrentCompletedSlide);
  };

  // Filter quests based on selected filter
  const filteredQuests = questFilter === 'all' 
    ? apiQuests 
    : apiQuests.filter(q => q.quest_type === questFilter);
  
  const activeQuests = filteredQuests.filter((q) => q.status === 'pending' || q.status === 'in_progress');
  const completedQuests = filteredQuests.filter((q) => q.status === 'completed');

  if (!user) {
    return null;
  }

  // Use backend stats if available, otherwise show loading state
  const stats = userStats ? [
    {
      icon: Flame,
      label: 'Streak',
      value: `${userStats.streak_days} days`,
      color: '#F59E0B',
    },
    {
      icon: Target,
      label: 'Completed',
      value: userStats.quests_completed,
      color: '#3B82F6',
    },
    {
      icon: Zap,
      label: 'Total XP',
      value: userStats.total_xp,
      color: '#06B6D4',
    },
  ] : [
    {
      icon: Flame,
      label: 'Streak',
      value: '0 days',
      color: '#F59E0B',
    },
    {
      icon: Target,
      label: 'Completed',
      value: 0,
      color: '#3B82F6',
    },
    {
      icon: Zap,
      label: 'Total XP',
      value: 0,
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
              level={userStats?.level || 1}
              totalXP={userStats?.total_xp || 0}
            />

            {/* Sync Emails Button */}
            <motion.button
              onClick={handleSyncEmails}
              disabled={isSyncing || isLoading}
              className="w-full py-5 rounded-2xl gradient-bg shine-effect font-heading font-bold text-lg text-white shadow-2xl flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
              whileHover={{ scale: isSyncing ? 1 : 1.02 }}
              whileTap={{ scale: isSyncing ? 1 : 0.98 }}
              style={{
                boxShadow: '0 10px 40px -10px hsl(var(--glow-primary)), 0 0 60px -20px hsl(var(--glow-secondary))',
              }}
            >
              {isSyncing ? (
                <>
                  <RefreshCw className="w-6 h-6 animate-spin" />
                  Syncing Emails...
                </>
              ) : (
                <>
                  <Mail className="w-6 h-6" />
                  Sync Emails & Generate Quests
                </>
              )}
            </motion.button>

            {/* Quest Filter Tabs */}
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => setQuestFilter('all')}
                className={`px-4 py-2 rounded-lg font-heading font-semibold transition-all ${
                  questFilter === 'all'
                    ? 'bg-gradient-to-r from-primary to-secondary text-white'
                    : 'bg-white/5 text-white/70 hover:bg-white/10'
                }`}
              >
                All Quests
              </button>
              <button
                onClick={() => setQuestFilter('daily_task')}
                className={`px-4 py-2 rounded-lg font-heading font-semibold transition-all ${
                  questFilter === 'daily_task'
                    ? 'bg-gradient-to-r from-primary to-secondary text-white'
                    : 'bg-white/5 text-white/70 hover:bg-white/10'
                }`}
              >
                Daily Tasks
              </button>
              <button
                onClick={() => setQuestFilter('email_based')}
                className={`px-4 py-2 rounded-lg font-heading font-semibold transition-all ${
                  questFilter === 'email_based'
                    ? 'bg-gradient-to-r from-primary to-secondary text-white'
                    : 'bg-white/5 text-white/70 hover:bg-white/10'
                }`}
              >
                Email Quests
              </button>
            </div>

            {/* Active Quests */}
            {activeQuests.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-heading text-2xl font-bold text-white">
                    Active Quests
                  </h2>
                  {Math.ceil(activeQuests.length / 6) > 1 && (
                    <div className="flex gap-2">
                      <motion.button
                        onClick={() => scrollActiveQuests('left')}
                        disabled={currentActiveSlide === 0}
                        className="p-2 rounded-lg glass glass-hover text-white disabled:opacity-50 disabled:cursor-not-allowed"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <ChevronLeft className="w-5 h-5" />
                      </motion.button>
                      <motion.button
                        onClick={() => scrollActiveQuests('right')}
                        disabled={currentActiveSlide === Math.ceil(activeQuests.length / 6) - 1}
                        className="p-2 rounded-lg glass glass-hover text-white disabled:opacity-50 disabled:cursor-not-allowed"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <ChevronRight className="w-5 h-5" />
                      </motion.button>
                    </div>
                  )}
                </div>
                <div className="relative">
                  <div 
                    ref={activeScrollRef}
                    className="overflow-x-auto scrollbar-hide"
                  >
                    <div className="flex gap-6 pb-4" style={{ width: 'max-content' }}>
                      {Array.from({ length: Math.ceil(activeQuests.length / 6) }, (_, slideIndex) => (
                        <div
                          key={slideIndex}
                          className="grid grid-cols-3 gap-4 flex-shrink-0"
                          style={{ width: 'calc(100vw - 4rem)', maxWidth: '900px' }}
                        >
                          {activeQuests.slice(slideIndex * 6, (slideIndex + 1) * 6).map((quest, index) => (
                            <motion.div
                              key={quest.id}
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: index * 0.1 }}
                              className="h-60"
                            >
                              <QuestCard quest={quest} onComplete={handleCompleteQuest} />
                            </motion.div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Scroll indicators */}
                  {Math.ceil(activeQuests.length / 6) > 1 && (
                    <div className="flex justify-center mt-4 gap-2">
                      {Array.from({ length: Math.ceil(activeQuests.length / 6) }, (_, index) => (
                        <button
                          key={index}
                          onClick={() => scrollToSlide(activeScrollRef, index, setCurrentActiveSlide)}
                          className={`w-2 h-2 rounded-full transition-all ${
                            index === currentActiveSlide ? 'bg-white' : 'bg-white/30'
                          }`}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Completed Quests */}
            {completedQuests.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-heading text-2xl font-bold text-white">
                    Completed Quests
                  </h2>
                  {Math.ceil(completedQuests.length / 6) > 1 && (
                    <div className="flex gap-2">
                      <motion.button
                        onClick={() => scrollCompletedQuests('left')}
                        disabled={currentCompletedSlide === 0}
                        className="p-2 rounded-lg glass glass-hover text-white disabled:opacity-50 disabled:cursor-not-allowed"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <ChevronLeft className="w-5 h-5" />
                      </motion.button>
                      <motion.button
                        onClick={() => scrollCompletedQuests('right')}
                        disabled={currentCompletedSlide === Math.ceil(completedQuests.length / 6) - 1}
                        className="p-2 rounded-lg glass glass-hover text-white disabled:opacity-50 disabled:cursor-not-allowed"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <ChevronRight className="w-5 h-5" />
                      </motion.button>
                    </div>
                  )}
                </div>
                <div className="relative">
                  <div 
                    ref={completedScrollRef}
                    className="overflow-x-auto scrollbar-hide"
                  >
                    <div className="flex gap-6 pb-4" style={{ width: 'max-content' }}>
                      {Array.from({ length: Math.ceil(completedQuests.length / 6) }, (_, slideIndex) => (
                        <div
                          key={slideIndex}
                          className="grid grid-cols-3 gap-4 flex-shrink-0"
                          style={{ width: 'calc(100vw - 4rem)', maxWidth: '900px' }}
                        >
                          {completedQuests.slice(slideIndex * 6, (slideIndex + 1) * 6).map((quest, index) => (
                            <motion.div
                              key={quest.id}
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: index * 0.1 }}
                              className="h-40"
                            >
                              <QuestCard
                                quest={quest}
                                onComplete={() => {}}
                              />
                            </motion.div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Scroll indicators */}
                  {Math.ceil(completedQuests.length / 6) > 1 && (
                    <div className="flex justify-center mt-4 gap-2">
                      {Array.from({ length: Math.ceil(completedQuests.length / 6) }, (_, index) => (
                        <button
                          key={index}
                          onClick={() => scrollToSlide(completedScrollRef, index, setCurrentCompletedSlide)}
                          className={`w-2 h-2 rounded-full transition-all ${
                            index === currentCompletedSlide ? 'bg-white' : 'bg-white/30'
                          }`}
                        />
                      ))}
                    </div>
                  )}
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
                    Daily Tasks
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {userPreferences?.daily_tasks?.map((task, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 rounded-lg gradient-bg text-white font-body text-sm font-semibold"
                      >
                        {task}
                      </span>
                    )) || (
                      <span className="text-muted-foreground text-sm">Loading...</span>
                    )}
                  </div>
                </div>
                
                <div>
                  <p className="text-muted-foreground text-sm font-body mb-2">
                    Long-term Goals
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {userPreferences?.long_term_goals?.map((goal, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 rounded-lg gradient-bg text-white font-body text-sm font-semibold"
                      >
                        {goal}
                      </span>
                    )) || (
                      <span className="text-muted-foreground text-sm">Loading...</span>
                    )}
                  </div>
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

      {/* Quest Chat */}
      <QuestChat />
    </div>
  );
}
