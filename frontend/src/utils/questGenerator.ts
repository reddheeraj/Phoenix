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
    status: 'active' as const,
    focusArea: template.focusArea,
    difficulty: template.difficulty,
    createdAt: new Date(),
  }));
}

export function calculateLevel(totalXP: number): number {
  return Math.floor(totalXP / 100) + 1;
}

export function getXPForNextLevel(currentLevel: number): number {
  // XP required to reach the NEXT level (level + 1) * 100
  return (currentLevel + 1) * 100;
}

export function getCurrentLevelXP(totalXP: number): number {
  return totalXP % 100;
}

export function getXPPercentage(totalXP: number, currentLevel: number): number {
  const currentLevelXP = getCurrentLevelXP(totalXP);
  const xpForNext = getXPForNextLevel(currentLevel);
  return (currentLevelXP / xpForNext) * 100;
}
