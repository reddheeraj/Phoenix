import { Card, CardContent } from "@/components/ui/card";
import { ReactNode } from "react";

/**
 * StatsCard Component
 * 
 * Displays a single stat from the user profile
 * Maps to the stats shown in Menu Option 5 (View Profile Summary) in main.py
 */
interface StatsCardProps {
  title: string;
  value: number;
  icon: ReactNode;
  color?: string;
}

export default function StatsCard({ title, value, icon, color = "text-blue-500" }: StatsCardProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-3xl font-bold mt-2">{value.toLocaleString()}</p>
          </div>
          <div className={`${color} opacity-80`}>{icon}</div>
        </div>
      </CardContent>
    </Card>
  );
}

