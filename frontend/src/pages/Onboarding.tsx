import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { BookOpen, Dumbbell, Briefcase, Gamepad2, Zap, Flame, ArrowRight, ArrowLeft, Target, Trophy } from 'lucide-react';
import { FloatingOrbs } from '@/components/FloatingOrbs';
import { PreferenceCard } from '@/components/PreferenceCard';
import { useUserStore } from '@/store/userStore';
import { useApiStore } from '@/store/apiStore';
import { FocusArea, Difficulty } from '@/types/quest';
import { toast } from 'sonner';

export default function Onboarding() {
  const navigate = useNavigate();
  const { user, setPreferences } = useUserStore();
  const { completeOnboarding, isLoading } = useApiStore();
  const [step, setStep] = useState(1);
  const [selectedFocusAreas, setSelectedFocusAreas] = useState<FocusArea[]>([]);
  const [selectedDifficulty, setSelectedDifficulty] = useState<Difficulty | null>(null);
  const [dailyTasks, setDailyTasks] = useState<string[]>([]);
  const [longTermGoals, setLongTermGoals] = useState<string[]>([]);

  const focusOptions = [
    {
      id: 'study' as FocusArea,
      title: 'Study',
      description: 'Academic goals and learning',
      icon: BookOpen,
      color: '#3B82F6',
    },
    {
      id: 'fitness' as FocusArea,
      title: 'Fitness',
      description: 'Health and exercise goals',
      icon: Dumbbell,
      color: '#10B981',
    },
    {
      id: 'productivity' as FocusArea,
      title: 'Productivity',
      description: 'Work and personal projects',
      icon: Briefcase,
      color: '#8B5CF6',
    },
  ];

  const difficultyOptions = [
    {
      id: 'casual' as Difficulty,
      title: 'Casual',
      description: 'Light quests, easy progress',
      icon: Gamepad2,
      color: '#10B981',
    },
    {
      id: 'balanced' as Difficulty,
      title: 'Balanced',
      description: 'Moderate challenge, steady growth',
      icon: Zap,
      color: '#F59E0B',
    },
    {
      id: 'hardcore' as Difficulty,
      title: 'Hardcore',
      description: 'Maximum challenge, epic rewards',
      icon: Flame,
      color: '#EF4444',
    },
  ];

  const toggleFocusArea = (area: FocusArea) => {
    setSelectedFocusAreas((prev) =>
      prev.includes(area) ? prev.filter((a) => a !== area) : [...prev, area]
    );
  };

  const handleNext = () => {
    if (step === 1 && selectedFocusAreas.length === 0) {
      toast.error('Please select at least one focus area');
      return;
    }
    if (step === 2 && !selectedDifficulty) {
      toast.error('Please select a difficulty level');
      return;
    }
    if (step === 3 && dailyTasks.length === 0) {
      toast.error('Please select at least one daily task');
      return;
    }
    if (step === 4 && longTermGoals.length === 0) {
      toast.error('Please select at least one long-term goal');
      return;
    }
    if (step < 5) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleComplete = async () => {
    console.log('handleComplete', user, dailyTasks, longTermGoals);
    if (!user || dailyTasks.length === 0 || longTermGoals.length === 0) {
      toast.error('Please complete all steps');
      return;
    }

    try {
      const result = await completeOnboarding({
        user_id: user.email, // Using email as user ID
        daily_tasks: dailyTasks,
        long_term_goals: longTermGoals,
      });

      if (result) {
        // Also set legacy preferences for backward compatibility
        setPreferences({
          focusAreas: selectedFocusAreas,
          difficulty: selectedDifficulty || 'balanced',
        });

        toast.success('Onboarding completed! Let\'s start your adventure!');
        navigate('/dashboard');
      }
    } catch (error) {
      toast.error('Failed to complete onboarding. Please try again.');
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      <FloatingOrbs />

      <div className="container mx-auto px-4 py-16 relative z-10">
        {/* Progress Indicators */}
        <div className="flex justify-center gap-2 mb-12">
          {[1, 2, 3, 4, 5].map((num) => (
            <motion.div
              key={num}
              className={`w-3 h-3 rounded-full ${
                num === step ? 'bg-primary' : 'bg-white/20'
              }`}
              animate={num === step ? { scale: [1, 1.3, 1] } : {}}
              transition={{ duration: 1, repeat: Infinity }}
            />
          ))}
        </div>

        <div className="max-w-4xl mx-auto">
          <AnimatePresence mode="wait">
            {/* Step 1: Focus Areas */}
            {step === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.3 }}
              >
                <h2 className="font-heading text-4xl md:text-5xl font-bold text-white text-center mb-4">
                  Choose Your Path
                </h2>
                <p className="text-muted-foreground text-center mb-12 font-body text-lg">
                  Select one or more focus areas for your quests
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {focusOptions.map((option) => (
                    <PreferenceCard
                      key={option.id}
                      title={option.title}
                      description={option.description}
                      icon={option.icon}
                      selected={selectedFocusAreas.includes(option.id)}
                      onClick={() => toggleFocusArea(option.id)}
                      color={option.color}
                    />
                  ))}
                </div>
              </motion.div>
            )}

            {/* Step 2: Difficulty */}
            {step === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.3 }}
              >
                <h2 className="font-heading text-4xl md:text-5xl font-bold text-white text-center mb-4">
                  Select Difficulty
                </h2>
                <p className="text-muted-foreground text-center mb-12 font-body text-lg">
                  Choose your challenge level
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {difficultyOptions.map((option) => (
                    <PreferenceCard
                      key={option.id}
                      title={option.title}
                      description={option.description}
                      icon={option.icon}
                      selected={selectedDifficulty === option.id}
                      onClick={() => setSelectedDifficulty(option.id)}
                      color={option.color}
                    />
                  ))}
                </div>
              </motion.div>
            )}

            {/* Step 3: Daily Tasks */}
            {step === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.3 }}
              >
                <h2 className="font-heading text-4xl md:text-5xl font-bold text-white text-center mb-4">
                  Daily Tasks
                </h2>
                <p className="text-muted-foreground text-center mb-12 font-body text-lg">
                  What do you want to do every day?
                </p>

                <div className="max-w-2xl mx-auto">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    {['Gym', 'Read', 'Code', 'Meditate', 'Walk', 'Learn'].map((task) => (
                      <motion.button
                        key={task}
                        onClick={() => {
                          if (dailyTasks.includes(task)) {
                            setDailyTasks(dailyTasks.filter(t => t !== task));
                          } else {
                            setDailyTasks([...dailyTasks, task]);
                          }
                        }}
                        className={`p-4 rounded-xl font-body font-semibold transition-all ${
                          dailyTasks.includes(task)
                            ? 'gradient-bg text-white'
                            : 'glass glass-hover text-white'
                        }`}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        {task}
                      </motion.button>
                    ))}
                  </div>

                  {dailyTasks.length > 0 && (
                    <div className="mt-6">
                      <h3 className="font-heading font-bold text-white mb-3">Selected Tasks:</h3>
                      <div className="flex flex-wrap gap-2">
                        {dailyTasks.map((task) => (
                          <span
                            key={task}
                            className="px-4 py-2 rounded-xl gradient-bg font-body font-semibold text-white text-sm"
                          >
                            {task}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {/* Step 4: Long-term Goals */}
            {step === 4 && (
              <motion.div
                key="step4"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.3 }}
              >
                <h2 className="font-heading text-4xl md:text-5xl font-bold text-white text-center mb-4">
                  Long-term Goals
                </h2>
                <p className="text-muted-foreground text-center mb-12 font-body text-lg">
                  What are your big dreams and aspirations?
                </p>

                <div className="max-w-2xl mx-auto">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    {['Get a Job', 'Learn AI', 'Save Money', 'Travel', 'Start Business', 'Get Fit'].map((goal) => (
                      <motion.button
                        key={goal}
                        onClick={() => {
                          if (longTermGoals.includes(goal)) {
                            setLongTermGoals(longTermGoals.filter(g => g !== goal));
                          } else {
                            setLongTermGoals([...longTermGoals, goal]);
                          }
                        }}
                        className={`p-4 rounded-xl font-body font-semibold transition-all ${
                          longTermGoals.includes(goal)
                            ? 'gradient-bg text-white'
                            : 'glass glass-hover text-white'
                        }`}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        {goal}
                      </motion.button>
                    ))}
                  </div>

                  {longTermGoals.length > 0 && (
                    <div className="mt-6">
                      <h3 className="font-heading font-bold text-white mb-3">Selected Goals:</h3>
                      <div className="flex flex-wrap gap-2">
                        {longTermGoals.map((goal) => (
                          <span
                            key={goal}
                            className="px-4 py-2 rounded-xl gradient-bg font-body font-semibold text-white text-sm"
                          >
                            {goal}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {/* Step 5: Confirmation */}
            {step === 5 && (
              <motion.div
                key="step5"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.3 }}
              >
                <h2 className="font-heading text-4xl md:text-5xl font-bold text-white text-center mb-4">
                  Ready to Begin?
                </h2>
                <p className="text-muted-foreground text-center mb-12 font-body text-lg">
                  Review your selections
                </p>

                <div className="glass rounded-2xl p-8 max-w-md mx-auto relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-secondary/10 -z-10" />

                  <div className="space-y-6">
                    <div>
                      <h3 className="font-heading font-bold text-white mb-3">
                        Daily Tasks
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {dailyTasks.map((task) => (
                          <span
                            key={task}
                            className="px-4 py-2 rounded-xl gradient-bg font-body font-semibold text-white text-sm"
                          >
                            {task}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="font-heading font-bold text-white mb-3">
                        Long-term Goals
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {longTermGoals.map((goal) => (
                          <span
                            key={goal}
                            className="px-4 py-2 rounded-xl gradient-bg font-body font-semibold text-white text-sm"
                          >
                            {goal}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Navigation Buttons */}
          <div className="flex justify-between items-center mt-12 max-w-2xl mx-auto">
            <motion.button
              onClick={handleBack}
              disabled={step === 1}
              className={`flex items-center gap-2 px-6 py-3 rounded-xl font-heading font-semibold transition-all ${
                step === 1
                  ? 'opacity-0 pointer-events-none'
                  : 'glass glass-hover text-white'
              }`}
              whileHover={step !== 1 ? { scale: 1.05 } : {}}
              whileTap={step !== 1 ? { scale: 0.95 } : {}}
            >
              <ArrowLeft className="w-5 h-5" />
              Back
            </motion.button>

            {step < 5 ? (
              <motion.button
                onClick={handleNext}
                className="flex items-center gap-2 px-6 py-3 rounded-xl font-heading font-semibold gradient-bg shine-effect text-white shadow-lg"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                style={{ boxShadow: '0 10px 30px -10px hsl(var(--glow-primary))' }}
                disabled={isLoading}
              >
                {isLoading ? 'Loading...' : 'Next'}
                {!isLoading && <ArrowRight className="w-5 h-5" />}
              </motion.button>
            ) : (
              <motion.button
                onClick={handleComplete}
                className="px-8 py-3 rounded-xl font-heading font-bold text-lg gradient-bg shine-effect text-white shadow-lg"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                style={{ boxShadow: '0 10px 30px -10px hsl(var(--glow-primary))' }}
                disabled={isLoading}
              >
                {isLoading ? 'Setting up...' : 'Start Adventure!'}
              </motion.button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
