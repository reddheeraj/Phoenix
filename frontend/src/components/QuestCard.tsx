import { motion } from 'framer-motion';
import { Zap, Trophy, Mail, Calendar, Info } from 'lucide-react';
import { ApiQuest } from '@/types/quest';
import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

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

// XP calculation based on quest type, importance and urgency (matches backend)
const calculateXP = (questType: string, importance: string, urgency: string): number => {
  const baseXP = {
    'daily_task': 10,
    'email_based': 25
  };
  
  const importanceMultiplier = {
    'daily': 1.0,
    'weekly': 1.2,
    'main_quest': 1.5,
    'side_quest': 0.8
  };
  
  const urgencyMultiplier = {
    'low': 0.8,
    'medium': 1.0,
    'high': 1.3,
    'critical': 1.5
  };
  
  const base = baseXP[questType] || 20;
  const importanceMult = importanceMultiplier[importance] || 1.0;
  const urgencyMult = urgencyMultiplier[urgency] || 1.0;
  
  return Math.floor(base * importanceMult * urgencyMult);
};

export const QuestCard = ({ quest, onComplete }: QuestCardProps) => {
  const isCompleted = quest.status === 'completed';
  const urgencyColor = urgencyColors[quest.urgency];
  const rankDisplay = importanceRank[quest.importance];
  const xpReward = calculateXP(quest.quest_type, quest.importance, quest.urgency);

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: isCompleted ? 0.6 : 1, scale: 1 }}
            whileHover={isCompleted ? {} : { y: -2, scale: 1.02 }}
            transition={{ duration: 0.2 }}
            className={`glass rounded-xl p-4 relative h-full flex flex-col ${
              isCompleted ? '' : 'glass-hover cursor-pointer'
            }`}
            style={{
              boxShadow: isCompleted
                ? 'none'
                : `0 5px 15px -5px ${urgencyColor}40`,
            }}
          >
      {/* Rank Badge */}
      <div
        className="absolute -top-2 -right-2 w-8 h-8 rounded-full flex items-center justify-center font-heading font-bold text-sm shadow-lg"
        style={{
          backgroundColor: urgencyColor,
        }}
      >
        {rankDisplay}
      </div>

      {/* Quest Type Badge */}
      {quest.quest_type === 'email_based' && (
        <div className="absolute top-2 left-2">
          <Mail className="w-3 h-3 text-blue-400" />
        </div>
      )}

      {/* Quest Content */}
      <div className="flex-1 flex flex-col">
        <h3 className="font-heading font-bold text-sm text-foreground pr-6 mb-2 line-clamp-2">
          {quest.title}
        </h3>
        
        {/* XP Badge */}
        <div className="flex items-center gap-1 bg-accent/20 rounded-lg px-2 py-1 w-fit mb-3">
          <Zap className="w-3 h-3 fill-accent text-accent" />
          <span className="font-heading font-bold text-accent text-xs">
            {xpReward} XP
          </span>
        </div>

        {/* Complete Button / Status */}
        {isCompleted ? (
          <div className="flex items-center gap-1 text-green-500 font-heading font-semibold text-xs mt-auto">
            <Trophy className="w-4 h-4" />
            <span>Done!</span>
          </div>
        ) : (
          <div className="mt-auto space-y-2">
            {/* Info Button */}
            <Dialog>
              <DialogTrigger asChild>
                <motion.button
                  className="w-full flex items-center justify-center gap-1 px-2 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-semibold transition-all"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Info className="w-3 h-3" />
                  Details
                </motion.button>
              </DialogTrigger>
              <DialogContent className="glass border-white/20 max-w-md">
                <DialogHeader>
                  <DialogTitle className="text-white font-heading">
                    {quest.title}
                  </DialogTitle>
                </DialogHeader>
                <div className="space-y-4 text-white">
                  <p className="text-sm text-white/80">{quest.description}</p>
                  
                  {quest.deadline && (
                    <div className="flex items-center gap-2 text-sm text-white/60">
                      <Calendar className="w-4 h-4" />
                      <span>Due: {new Date(quest.deadline).toLocaleDateString()}</span>
                    </div>
                  )}
                  
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-white/60">Category:</span>
                    <span className="capitalize">{quest.quest_category}</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-white/60">Urgency:</span>
                    <span className="capitalize">{quest.urgency}</span>
                  </div>
                </div>
              </DialogContent>
            </Dialog>

            {/* Complete Button */}
            <motion.button
              onClick={() => onComplete(quest.id.toString())}
              className="w-full gradient-bg rounded-lg py-2 font-heading font-semibold text-white text-xs shadow-lg"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Complete
            </motion.button>
          </div>
        )}
      </div>
          </motion.div>
        </TooltipTrigger>
        <TooltipContent 
          side="top" 
          className="glass border-white/20 max-w-xs p-3"
          sideOffset={5}
        >
          <div className="space-y-2">
            <p className="text-sm text-white font-medium">{quest.title}</p>
            <p className="text-xs text-white/80">{quest.description}</p>
            {quest.deadline && (
              <div className="flex items-center gap-1 text-xs text-white/60">
                <Calendar className="w-3 h-3" />
                <span>Due: {new Date(quest.deadline).toLocaleDateString()}</span>
              </div>
            )}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};
