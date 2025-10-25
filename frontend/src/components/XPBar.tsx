import { motion } from 'framer-motion';
import { getXPPercentage, getCurrentLevelXP } from '@/utils/questGenerator';

interface XPBarProps {
  totalXP: number;
}

export const XPBar = ({ totalXP }: XPBarProps) => {
  const percentage = getXPPercentage(totalXP);
  const currentXP = getCurrentLevelXP(totalXP);

  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between items-center text-sm">
        <span className="text-muted-foreground font-body">XP Progress</span>
        <span className="font-heading text-foreground">
          {currentXP} / 100 XP
        </span>
      </div>
      
      <div className="relative h-8 bg-black/30 rounded-full border border-white/10 overflow-hidden">
        {/* XP Fill */}
        <motion.div
          className="absolute inset-y-0 left-0 gradient-bg shine-effect"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{
            boxShadow: '0 0 20px hsl(var(--glow-primary)), inset 0 2px 10px rgba(255,255,255,0.3)',
          }}
        />
        
        {/* Percentage Text */}
        <div className="relative h-full flex items-center justify-center">
          <span className="font-heading text-sm font-bold text-white drop-shadow-lg z-10">
            {Math.round(percentage)}%
          </span>
        </div>
      </div>
    </div>
  );
};
