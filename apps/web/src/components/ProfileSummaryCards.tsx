import React from 'react';
import { Database, LayoutGrid, Files, Hash } from 'lucide-react';
import { cn } from './UploadDropzone';

interface ProfileSummaryCardsProps {
  summary: any;
}

export const ProfileSummaryCards: React.FC<ProfileSummaryCardsProps> = ({ summary }) => {
  if (!summary) return null;

  return (
    <div className="w-full max-w-5xl mx-auto mt-8">
      <h2 className="text-xl font-semibold mb-6">Dataset Overview</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="Total Rows" 
          value={summary.total_rows?.toLocaleString()} 
          icon={<Database className="w-4 h-4" />} 
        />
        <MetricCard 
          title="Total Columns" 
          value={summary.total_columns?.toLocaleString()} 
          icon={<LayoutGrid className="w-4 h-4" />} 
        />
        <MetricCard 
          title="Duplicate Rows" 
          value={summary.duplicates_count?.toLocaleString()} 
          subValue={`${(summary.duplicates_percentage * 100).toFixed(2)}%`}
          icon={<Files className="w-4 h-4" />} 
          intent={summary.duplicates_count > 0 ? "warning" : "default"}
        />
        <MetricCard 
          title="Features" 
          value={`${Object.keys(summary.numeric_features || {}).length} Num / ${Object.keys(summary.categorical_features || {}).length} Cat`} 
          icon={<Hash className="w-4 h-4" />} 
        />
      </div>
      
      {/* Sample output for deeper metrics could go here */}
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: string | number;
  subValue?: string;
  icon: React.ReactNode;
  intent?: 'default' | 'warning' | 'danger';
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, subValue, icon, intent = 'default' }) => {
  return (
    <div className="p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
      <div className="flex items-center justify-between space-y-0 pb-2">
        <h3 className="tracking-tight text-sm font-medium text-muted-foreground">{title}</h3>
        <div className={cn(
          "p-2 rounded-md",
          intent === 'default' && "text-muted-foreground bg-secondary",
          intent === 'warning' && "text-amber-600 bg-amber-100 dark:bg-amber-900/30",
          intent === 'danger' && "text-destructive bg-destructive/10"
        )}>
          {icon}
        </div>
      </div>
      <div className="flex items-baseline gap-2">
        <div className="text-2xl font-bold">{value}</div>
        {subValue && (
          <span className={cn(
            "text-xs font-semibold",
            intent === 'default' && "text-muted-foreground",
            intent === 'warning' && "text-amber-600",
            intent === 'danger' && "text-destructive"
          )}>{subValue}</span>
        )}
      </div>
    </div>
  );
};
