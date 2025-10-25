import { motion } from 'framer-motion';
import { getAPPercentage, getCurrentLevelAP } from '@/utils/questGenerator';

interface APBarProps {
  totalAP: number;
}

export const APBar = ({ totalAP }: APBarProps) => {
  const percentage = getAPPercentage(totalAP);
  const currentAP = getCurrentLevelAP(totalAP);

  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between items-center text-sm">
        <span className="text-muted-foreground font-body">AP Progress</span>
        <span className="font-heading text-foreground">
          {currentAP} / 100 AP
        </span>
      </div>
      
      <div className="relative h-8 bg-black/30 rounded-full border border-white/10 overflow-hidden">
        {/* AP Fill */}
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
