import { motion } from 'framer-motion';

interface XPBarProps {
  totalXP: number;
  currentXP?: number;
  level?: number;
}

export const XPBar = ({ totalXP, currentXP, level }: XPBarProps) => {
  // Calculate XP required for next level using backend system (100 * level)
  const xpForNextLevel = level ? (level + 1) * 100 : 100;
  const xpForCurrentLevel = level ? level * 100 : 0;
  
  // Use currentXP from backend if available, otherwise calculate from totalXP
  const actualCurrentXP = currentXP !== undefined ? currentXP : (totalXP - xpForCurrentLevel);
  
  // Calculate percentage for current level progress
  const percentage = Math.min((actualCurrentXP / 100) * 100, 100);

  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between items-center text-sm">
        <span className="text-muted-foreground font-body">XP Progress</span>
        <span className="font-heading text-foreground">
          {actualCurrentXP} / 100 XP
        </span>
      </div>
      
      <div className="relative h-8 bg-black/30 rounded-full border border-white/10 overflow-hidden">
        {/* XP Fill */}
        <motion.div
          className="absolute inset-y-0 left-0 h-full gradient-bg shine-effect rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{
            boxShadow: '0 0 20px hsl(var(--glow-primary)), inset 0 2px 10px rgba(255,255,255,0.3)',
            background: 'linear-gradient(90deg, #6366F1 0%, #8B5CF6 50%, #06B6D4 100%)',
          }}
        />
        
        {/* Percentage Text */}
        <div className="relative h-full flex items-center justify-center z-10">
          <span className="font-heading text-sm font-bold text-white drop-shadow-lg">
            {Math.round(percentage)}%
          </span>
        </div>
      </div>
    </div>
  );
};
