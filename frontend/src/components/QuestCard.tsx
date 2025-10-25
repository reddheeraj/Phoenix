import { motion } from 'framer-motion';
import { Zap, Trophy } from 'lucide-react';
import { Quest } from '@/types/quest';

interface QuestCardProps {
  quest: Quest;
  onComplete: (questId: string) => void;
}

const rankColors = {
  E: 'hsl(var(--rank-e))',
  D: 'hsl(var(--rank-d))',
  C: 'hsl(var(--rank-c))',
  B: 'hsl(var(--rank-b))',
  A: 'hsl(var(--rank-a))',
  S: 'hsl(var(--rank-s))',
};

export const QuestCard = ({ quest, onComplete }: QuestCardProps) => {
  const isCompleted = quest.status === 'completed';
  const rankColor = rankColors[quest.rank];

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
          : `0 10px 30px -10px ${rankColor}40, 0 20px 50px -20px ${rankColor}20`,
      }}
    >
      {/* Rank Badge */}
      <motion.div
        className="absolute -top-3 -right-3 w-14 h-14 rounded-full flex items-center justify-center font-heading font-bold text-lg shadow-lg"
        style={{
          backgroundColor: rankColor,
          boxShadow: `0 0 20px ${rankColor}80, 0 0 40px ${rankColor}40`,
        }}
        whileHover={isCompleted ? {} : { rotate: [0, -10, 10, -10, 0] }}
        transition={{ duration: 0.5 }}
      >
        {quest.rank}
      </motion.div>

      {/* Quest Content */}
      <div className="space-y-3">
        <h3 className="font-heading font-bold text-xl text-foreground pr-8">
          {quest.title}
        </h3>
        
        <p className="text-muted-foreground font-body text-sm">
          {quest.description}
        </p>

        {/* AP Badge */}
        <div className="flex items-center gap-2 bg-accent/20 rounded-xl px-3 py-2 w-fit">
          <Zap className="w-4 h-4 fill-accent text-accent" />
          <span className="font-heading font-bold text-accent">
            {quest.xp} AP
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
            onClick={() => onComplete(quest.id)}
            className="w-full mt-4 gradient-bg shine-effect rounded-xl py-3 font-heading font-semibold text-white shadow-lg"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            style={{
              boxShadow: '0 10px 30px -10px hsl(var(--glow-primary))',
            }}
          >
            Complete Quest
          </motion.button>
        )}
      </div>
    </motion.div>
  );
};
