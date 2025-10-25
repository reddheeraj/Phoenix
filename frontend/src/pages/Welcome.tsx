import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import { Sword, Target, Zap, Trophy } from 'lucide-react';
import { FloatingOrbs } from '@/components/FloatingOrbs';
import { useUserStore } from '@/store/userStore';
import { useApiStore } from '@/store/apiStore';
import { toast } from 'sonner';

interface GoogleCredentialResponse {
  credential?: string;
}

interface DecodedToken {
  name: string;
  email: string;
  picture: string;
}

export default function Welcome() {
  const navigate = useNavigate();
  const { user, preferences, setUser } = useUserStore();
  const { fetchUserPreferences } = useApiStore();

  useEffect(() => {
    // If already logged in, check backend for user preferences
    if (user) {
      const checkUserPreferences = async () => {
        try {
          // Try to fetch user preferences from backend
          await fetchUserPreferences(user.email);
          // If successful, user exists in backend - go to dashboard
          navigate('/dashboard');
        } catch (error) {
          // If user doesn't exist in backend, go to onboarding
          console.log('User not found in backend, redirecting to onboarding');
          navigate('/onboarding');
        }
      };
      
      checkUserPreferences();
    }
  }, [user, navigate, fetchUserPreferences]);

  const handleGoogleSuccess = async (response: GoogleCredentialResponse) => {
    try {
      if (!response.credential) {
        throw new Error('No credential received');
      }

      const decoded = jwtDecode<DecodedToken>(response.credential);
      
      setUser(
        {
          name: decoded.name,
          email: decoded.email,
          picture: decoded.picture,
        },
        response.credential
      );

      toast.success(`Welcome, ${decoded.name}!`);

      // Check if user exists in backend
      try {
        await fetchUserPreferences(decoded.email);
        // User exists in backend - go to dashboard
        navigate('/dashboard');
      } catch (error) {
        // User doesn't exist in backend - go to onboarding
        console.log('New user, redirecting to onboarding');
        navigate('/onboarding');
      }
    } catch (error) {
      console.error('Google login error:', error);
      toast.error('Failed to sign in. Please try again.');
    }
  };

  const features = [
    {
      icon: Target,
      title: 'Daily Quests',
      description: 'Transform your tasks into exciting quests',
      gradient: 'from-blue-500 to-cyan-500',
    },
    {
      icon: Zap,
      title: 'Earn XP',
      description: 'Gain experience points for every completed quest',
      gradient: 'from-purple-500 to-pink-500',
    },
    {
      icon: Trophy,
      title: 'Level Up',
      description: 'Progress through levels and unlock achievements',
      gradient: 'from-orange-500 to-red-500',
    },
  ];

  return (
    <div className="min-h-screen relative overflow-hidden">
      <FloatingOrbs />

      <div className="container mx-auto px-4 py-16 relative z-10">
        {/* Hero Section */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Hero Icon */}
          <motion.div
            className="inline-flex items-center justify-center w-28 h-28 rounded-3xl gradient-bg mb-8 shadow-2xl"
            style={{ boxShadow: '0 0 40px hsl(var(--glow-primary)), 0 0 80px hsl(var(--glow-secondary))' }}
            animate={{
              rotate: [0, 360],
              scale: [1, 1.1, 1],
            }}
            transition={{
              rotate: { duration: 20, repeat: Infinity, ease: 'linear' },
              scale: { duration: 2, repeat: Infinity },
            }}
          >
            <Sword className="w-14 h-14 text-white" />
          </motion.div>

          {/* Title */}
          <h1 className="font-heading text-6xl md:text-8xl font-black mb-4">
            <span className="gradient-text">QUEST</span>
          </h1>
          <h2 className="font-heading text-4xl md:text-6xl font-bold text-white mb-6" style={{ textShadow: '0 0 30px rgba(255,255,255,0.3)' }}>
            LEVELING SYSTEM
          </h2>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-gray-400 max-w-2xl mx-auto font-body">
            Transform your daily tasks into epic quests. Earn XP, level up, and achieve your goals with an anime-inspired productivity system.
          </p>
        </motion.div>

        {/* Feature Cards */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16 max-w-6xl mx-auto"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, staggerChildren: 0.1 }}
        >
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              className="glass glass-hover rounded-2xl p-8 text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + index * 0.1 }}
              whileHover={{ y: -8, scale: 1.02 }}
            >
              <div
                className={`w-16 h-16 rounded-2xl bg-gradient-to-r ${feature.gradient} flex items-center justify-center mx-auto mb-4 shadow-lg`}
                style={{ boxShadow: '0 10px 30px -10px rgba(99, 102, 241, 0.5)' }}
              >
                <feature.icon className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-heading text-xl font-bold text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-muted-foreground font-body">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </motion.div>

        {/* Sign In Card */}
        <motion.div
          className="max-w-md mx-auto glass rounded-2xl p-8 text-center relative overflow-hidden"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.7 }}
        >
          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-secondary/10 to-primary/10 -z-10" />

          <h3 className="font-heading text-2xl font-bold text-white mb-6">
            Start Your Journey
          </h3>

          <div className="flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => {
                console.error('Google login failed');
                toast.error('Failed to sign in with Google');
              }}
              useOneTap
              theme="filled_black"
              size="large"
              shape="pill"
            />
          </div>
        </motion.div>
      </div>
    </div>
  );
}
