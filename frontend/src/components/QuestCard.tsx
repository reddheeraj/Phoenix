import { motion } from 'framer-motion';
import { Zap, Trophy, Mail, Calendar } from 'lucide-react';
import { ApiQuest } from '@/types/quest';

interface QuestCardProps {
  quest: ApiQuest;
  onComplete: (questId: string) => void;
}

// Map urgency to rank-like colors
const urgencyColors = {
  low: 'hsl(var(--rank-e))',     // Green
  medium: 'hsl(var(--rank-c))',  // Yellow
  high: 'hsl(var(--rank-a))',    // Orange
  critical: 'hsl(var(--rank-s))', // Red
};

// Map importance to rank display
const importanceRank = {
  daily: 'D',
  weekly: 'W',
  side_quest: 'S',
  main_quest: 'M',
};

// XP calculation based on importance and urgency
const calculateXP = (importance: string, urgency: string): number => {
  const importanceXP = {
    daily: 25,
    weekly: 50,
    side_quest: 100,
    main_quest: 200,
  };
  
  const urgencyMultiplier = {
    low: 1,
    medium: 1.5,
    high: 2,
    critical: 3,
  };
  
  return Math.floor((importanceXP[importance] || 25) * (urgencyMultiplier[urgency] || 1));
};

export const QuestCard = ({ quest, onComplete }: QuestCardProps) => {
  const isCompleted = quest.status === 'completed';
  const urgencyColor = urgencyColors[quest.urgency];
  const rankDisplay = importanceRank[quest.importance];
  const xpReward = calculateXP(quest.importance, quest.urgency);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: isCompleted ? 0.6 : 1, scale: 1 }}
      whileHover={isCompleted ? {} : { y: -5, scale: 1.03 }}
      transition={{ duration: 0.3 }}
      className={`glass rounded-2xl p-6 relative ${
        isCompleted ? '' : 'glass-hover cursor-pointer'
      }`}
      style={{
        boxShadow: isCompleted
          ? 'none'
          : `0 10px 30px -10px ${urgencyColor}40, 0 20px 50px -20px ${urgencyColor}20`,
      }}
    >
      {/* Rank Badge */}
      <motion.div
        className="absolute -top-3 -right-3 w-14 h-14 rounded-full flex items-center justify-center font-heading font-bold text-lg shadow-lg"
        style={{
          backgroundColor: urgencyColor,
          boxShadow: `0 0 20px ${urgencyColor}80, 0 0 40px ${urgencyColor}40`,
        }}
        whileHover={isCompleted ? {} : { rotate: [0, -10, 10, -10, 0] }}
        transition={{ duration: 0.5 }}
      >
        {rankDisplay}
      </motion.div>

      {/* Quest Type Badge */}
      {quest.quest_type === 'email_based' && (
        <div className="absolute top-3 left-3 flex items-center gap-1 px-2 py-1 rounded-lg bg-blue-500/20 border border-blue-500/30">
          <Mail className="w-3 h-3 text-blue-400" />
          <span className="text-xs font-semibold text-blue-400">Email</span>
        </div>
      )}

      {/* Quest Content */}
      <div className={`space-y-3 ${quest.quest_type === 'email_based' ? 'mt-6' : ''}`}>
        <h3 className="font-heading font-bold text-xl text-foreground pr-8">
          {quest.title}
        </h3>
        
        <p className="text-muted-foreground font-body text-sm">
          {quest.description}
        </p>
        
        {/* Deadline */}
        {quest.deadline && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Calendar className="w-3 h-3" />
            <span>Due: {new Date(quest.deadline).toLocaleDateString()}</span>
          </div>
        )}

        {/* XP Badge */}
        <div className="flex items-center gap-2 bg-accent/20 rounded-xl px-3 py-2 w-fit">
          <Zap className="w-4 h-4 fill-accent text-accent" />
          <span className="font-heading font-bold text-accent">
            {xpReward} XP
          </span>
        </div>

        {/* Complete Button / Status */}
        {isCompleted ? (
          <div className="flex items-center gap-2 text-green-500 font-heading font-semibold">
            <Trophy className="w-5 h-5" />
            <span>Completed!</span>
          </div>
        ) : (
          <motion.button
            onClick={() => onComplete(quest.id.toString())}
            className="w-full mt-4 gradient-bg shine-effect rounded-xl py-3 font-heading font-semibold text-white shadow-lg"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            style={{
              boxShadow: `0 10px 30px -10px ${urgencyColor}60`,
            }}
          >
            Complete Quest
          </motion.button>
        )}
      </div>
    </motion.div>
  );
};
