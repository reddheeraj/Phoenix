import { Quest, FocusArea, Difficulty } from '@/types/quest';
import { questTemplates } from '@/data/questTemplates';

export function generateQuests(
  focusAreas: FocusArea[],
  difficulty: Difficulty,
  count: number = 5
): Quest[] {
  // Filter templates by user preferences
  const availableTemplates = questTemplates.filter(
    (template) =>
      focusAreas.includes(template.focusArea) &&
      template.difficulty === difficulty
  );

  // Shuffle templates
  const shuffled = [...availableTemplates].sort(() => Math.random() - 0.5);

  // Take requested count and create quest objects
  const selectedTemplates = shuffled.slice(0, Math.min(count, shuffled.length));

  return selectedTemplates.map((template, index) => ({
    id: `quest-${Date.now()}-${index}`,
    title: template.title,
    description: template.description,
    rank: template.rank,
    xp: template.xp,
    status: 'pending' as const,
    focusArea: template.focusArea,
    difficulty: template.difficulty,
    createdAt: new Date(),
  }));
}

export function calculateLevel(totalXP: number): number {
  return Math.floor(totalXP / 100) + 1;
}

export function getXPForNextLevel(currentLevel: number): number {
  return currentLevel * 100;
}

export function getCurrentLevelXP(totalXP: number): number {
  return totalXP % 100;
}

export function getXPPercentage(totalXP: number): number {
  const currentLevelXP = getCurrentLevelXP(totalXP);
  return (currentLevelXP / 100) * 100;
}

// AP versions (same implementation, different names for display purposes)
export function getCurrentLevelAP(totalAP: number): number {
  return totalAP % 100;
}

export function getAPPercentage(totalAP: number): number {
  const currentLevelAP = getCurrentLevelAP(totalAP);
  return (currentLevelAP / 100) * 100;
}
