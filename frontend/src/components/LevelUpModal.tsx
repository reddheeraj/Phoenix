import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles } from 'lucide-react';
import confetti from 'canvas-confetti';

interface LevelUpModalProps {
  isOpen: boolean;
  level: number;
  onClose: () => void;
}

export const LevelUpModal = ({ isOpen, level, onClose }: LevelUpModalProps) => {
  useEffect(() => {
    if (isOpen) {
      // Fire confetti
      const duration = 3000;
      const end = Date.now() + duration;

      const frame = () => {
        confetti({
          particleCount: 3,
          angle: 60,
          spread: 55,
          origin: { x: 0 },
          colors: ['#6366F1', '#8B5CF6', '#06B6D4'],
        });
        confetti({
          particleCount: 3,
          angle: 120,
          spread: 55,
          origin: { x: 1 },
          colors: ['#6366F1', '#8B5CF6', '#06B6D4'],
        });

        if (Date.now() < end) {
          requestAnimationFrame(frame);
        }
      };

      frame();
    }
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            className="relative glass rounded-2xl p-12 text-center max-w-md w-full"
            style={{
              background: 'linear-gradient(to bottom right, hsl(var(--primary)), hsl(var(--secondary)))',
              boxShadow: '0 0 60px hsl(var(--glow-primary)), 0 0 100px hsl(var(--glow-secondary))',
            }}
            initial={{ opacity: 0, scale: 0.8, rotateY: -30 }}
            animate={{ opacity: 1, scale: 1, rotateY: 0 }}
            exit={{ opacity: 0, scale: 0.8, rotateY: 30 }}
            transition={{ type: 'spring', duration: 0.6 }}
          >
            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 w-8 h-8 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors"
            >
              <X className="w-5 h-5 text-white" />
            </button>

            {/* Sparkles Icon */}
            <motion.div
              className="flex justify-center mb-6"
              animate={{
                rotate: 360,
                scale: [1, 1.2, 1],
              }}
              transition={{
                rotate: { duration: 2, repeat: Infinity, ease: 'linear' },
                scale: { duration: 1, repeat: Infinity },
              }}
            >
              <Sparkles className="w-16 h-16 text-white fill-white" />
            </motion.div>

            {/* Level Up Text */}
            <h2 className="font-heading text-5xl font-black text-white mb-4" style={{ textShadow: '0 0 30px rgba(255,255,255,0.5)' }}>
              LEVEL UP!
            </h2>

            {/* New Level */}
            <motion.div
              className="font-heading text-8xl font-black text-white mb-6"
              animate={{
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
              }}
            >
              {level}
            </motion.div>

            {/* Message */}
            <p className="text-white/90 font-body text-lg mb-8">
              You've reached Level {level}! Your dedication is paying off. Keep pushing forward!
            </p>

            {/* Continue Button */}
            <motion.button
              onClick={onClose}
              className="bg-white text-primary font-heading font-bold py-3 px-8 rounded-xl shadow-lg"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Continue
            </motion.button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
