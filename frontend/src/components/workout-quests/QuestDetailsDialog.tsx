import { Quest } from "@/lib/api/workout-quests";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Zap, Coins, Gift, Dumbbell, Clock } from "lucide-react";

/**
 * QuestDetailsDialog Component
 * 
 * Shows detailed quest information in a modal
 * Maps to Menu Option 2 (View Quest Details) from main.py
 * Displays same information as quest_manager.get_quest_details()
 */
interface QuestDetailsDialogProps {
  quest: Quest;
  open: boolean;
  onClose: () => void;
  onComplete?: () => void;
}

export default function QuestDetailsDialog({
  quest,
  open,
  onClose,
  onComplete,
}: QuestDetailsDialogProps) {
  const isCompleted = quest.status === "completed";

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh]">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div>
              <DialogTitle className="text-2xl">{quest.title}</DialogTitle>
              <DialogDescription className="mt-2">{quest.description}</DialogDescription>
            </div>
            <Badge variant={isCompleted ? "secondary" : "default"}>
              {isCompleted ? "Completed" : "Active"}
            </Badge>
          </div>
        </DialogHeader>

        <ScrollArea className="max-h-[60vh] pr-4">
          <div className="space-y-6">
            {/* Rewards Section - Maps to rewards display in main.py */}
            <div>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Gift className="h-5 w-5" />
                Rewards
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="flex items-center gap-2 p-3 bg-purple-500/10 rounded-lg border border-purple-500/20">
                  <Zap className="h-5 w-5 text-purple-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Experience</p>
                    <p className="font-bold">{quest.experience_reward} XP</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 p-3 bg-amber-500/10 rounded-lg border border-amber-500/20">
                  <Coins className="h-5 w-5 text-amber-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Coins</p>
                    <p className="font-bold">{quest.coin_reward}</p>
                  </div>
                </div>
              </div>

              {/* Special Rewards - Maps to cached_rewards in main.py */}
              {quest.cached_rewards.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm font-medium mb-2">Special Rewards:</p>
                  <div className="space-y-2">
                    {quest.cached_rewards.map((reward, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-pink-500/10 rounded-lg border border-pink-500/20"
                      >
                        <p className="font-medium">
                          {reward.merchant || reward.store || "Special Offer"}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {reward.offer || reward.discount || "Exclusive reward"}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <Separator />

            {/* Exercises Section - Maps to workout_day.exercises in main.py */}
            <div>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Dumbbell className="h-5 w-5" />
                Exercises ({quest.exercises.length})
              </h3>
              <div className="space-y-4">
                {quest.exercises.map((exercise, idx) => (
                  <div key={idx} className="p-4 border rounded-lg space-y-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium">{idx + 1}. {exercise.name}</h4>
                        <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
                          <span className="capitalize">{exercise.muscle}</span>
                          <span>•</span>
                          <span className="capitalize">{exercise.equipment}</span>
                          <span>•</span>
                          <Badge variant="outline" className="capitalize">
                            {exercise.difficulty}
                          </Badge>
                        </div>
                      </div>
                    </div>

                    {/* Exercise Details - Maps to sets, reps, rest in main.py */}
                    <div className="flex items-center gap-4 text-sm mt-2">
                      <div className="flex items-center gap-1">
                        <span className="font-semibold">{exercise.sets}</span>
                        <span className="text-muted-foreground">sets</span>
                      </div>
                      <span className="text-muted-foreground">×</span>
                      <div className="flex items-center gap-1">
                        <span className="font-semibold">{exercise.reps}</span>
                        <span className="text-muted-foreground">reps</span>
                      </div>
                      <span className="text-muted-foreground">•</span>
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span className="font-semibold">{exercise.rest_seconds}s</span>
                        <span className="text-muted-foreground">rest</span>
                      </div>
                    </div>

                    {/* Exercise Instructions - Maps to exercise.instructions in main.py */}
                    {exercise.instructions && (
                      <div className="mt-2 p-3 bg-muted/50 rounded text-sm">
                        <p className="font-medium mb-1">Instructions:</p>
                        <p className="text-muted-foreground leading-relaxed">
                          {exercise.instructions}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </ScrollArea>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
          {/* Complete Quest Button - Maps to Menu Option 3 in main.py */}
          {onComplete && !isCompleted && (
            <Button onClick={onComplete}>Mark as Complete</Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

