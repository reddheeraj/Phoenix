import { motion } from 'framer-motion';
import { LucideIcon, Check } from 'lucide-react';

interface PreferenceCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  selected: boolean;
  onClick: () => void;
  color: string;
}

export const PreferenceCard = ({
  title,
  description,
  icon: Icon,
  selected,
  onClick,
  color,
}: PreferenceCardProps) => {
  return (
    <motion.button
      onClick={onClick}
      className={`glass rounded-2xl p-8 text-center transition-all duration-300 relative overflow-hidden ${
        selected ? 'border-white/50' : 'border-white/10 glass-hover'
      }`}
      style={{
        background: selected
          ? `linear-gradient(to bottom right, ${color}20, ${color}10)`
          : undefined,
      }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Checkmark */}
      {selected && (
        <motion.div
          className="absolute top-4 right-4 w-8 h-8 rounded-full bg-gradient-to-r from-primary to-secondary flex items-center justify-center"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
        >
          <Check className="w-5 h-5 text-white" />
        </motion.div>
      )}

      {/* Icon */}
      <div
        className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg"
        style={{
          backgroundColor: `${color}40`,
          boxShadow: `0 10px 30px -10px ${color}60`,
        }}
      >
        <Icon className="w-8 h-8 text-white" />
      </div>

      {/* Content */}
      <h3 className="font-heading text-xl font-bold text-foreground mb-2">
        {title}
      </h3>
      <p className="text-muted-foreground font-body text-sm">
        {description}
      </p>
    </motion.button>
  );
};
