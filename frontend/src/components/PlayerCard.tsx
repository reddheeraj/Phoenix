import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';
import { XPBar } from './XPBar';

interface PlayerCardProps {
  name: string;
  picture: string;
  level: number;
  totalXP: number;
}

export const PlayerCard = ({ name, picture, level, totalXP }: PlayerCardProps) => {
  return (
    <div className="glass glass-hover rounded-2xl p-8 relative overflow-hidden">
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-secondary/10 -z-10" />

      <div className="flex items-center gap-6 mb-6">
        {/* Avatar with Glow */}
        <motion.div
          className="relative"
          whileHover={{ scale: 1.05 }}
          transition={{ duration: 0.3 }}
        >
          {/* Glow Effect */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-r from-primary to-secondary blur-md opacity-50" />
          
          {/* Avatar */}
          <img
            src={picture}
            alt={name}
            className="w-24 h-24 rounded-full border-2 border-white/30 relative z-10"
          />

          {/* Level Badge */}
          <motion.div
            className="absolute -bottom-2 -right-2 w-12 h-12 rounded-full gradient-bg flex items-center justify-center shadow-lg z-20"
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
          >
            <div className="flex flex-col items-center">
              <Sparkles className="w-3 h-3 fill-white text-white" />
              <span className="font-heading text-xs font-bold text-white">
                {level}
              </span>
            </div>
          </motion.div>
        </motion.div>

        {/* Player Info */}
        <div className="flex-1">
          <h2 className="font-heading text-3xl font-bold text-foreground mb-1">
            {name}
          </h2>
          <p className="text-muted-foreground font-body">
            Level {level} Adventurer
          </p>
        </div>
      </div>

      {/* XP Bar */}
      <XPBar totalXP={totalXP} />
    </div>
  );
};
