import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';
import { APBar } from './XPBar';

interface PlayerCardProps {
  name: string;
  picture: string;
  level: number;
  totalAP: number;
}

export const PlayerCard = ({ name, picture, level, totalAP }: PlayerCardProps) => {
  return (
    <div className="glass glass-hover rounded-2xl p-8 relative overflow-hidden">
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-secondary/10 -z-10" />

      {/* Stylish Level Badge - Top Right */}
      <motion.div
        className="absolute top-6 right-6 flex items-center gap-3 px-5 py-3 rounded-2xl gradient-bg shadow-2xl"
        initial={{ opacity: 0, scale: 0.8, x: 20 }}
        animate={{ opacity: 1, scale: 1, x: 0 }}
        whileHover={{ scale: 1.05 }}
        transition={{ duration: 0.3 }}
        style={{
          boxShadow: '0 0 30px hsl(var(--glow-primary)), 0 10px 40px -10px hsl(var(--glow-secondary))',
        }}
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
        >
          <Sparkles className="w-5 h-5 fill-white text-white" />
        </motion.div>
        <div className="flex flex-col items-center gap-0.5">
          <span className="text-white/80 text-xs font-body uppercase tracking-wider">Level</span>
          <span className="font-heading text-2xl font-black text-white leading-none">
            {level}
          </span>
        </div>
      </motion.div>

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
        </motion.div>

        {/* Player Info */}
        <div className="flex-1">
          <h2 className="font-heading text-3xl font-bold text-foreground mb-1">
            {name}
          </h2>
          <p className="text-muted-foreground font-body">
            Adventurer
          </p>
        </div>
      </div>

      {/* AP Bar */}
      <APBar totalAP={totalAP} />
    </div>
  );
};
