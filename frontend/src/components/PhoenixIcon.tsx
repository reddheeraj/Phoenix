import { SVGProps } from 'react';

export const PhoenixIcon = (props: SVGProps<SVGSVGElement>) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      {/* Phoenix head and body */}
      <path d="M12 2 L13 4 L12 6 L11 4 Z" />
      
      {/* Left wing */}
      <path d="M11 6 Q8 8 6 12 Q5 14 4 16 L5 17 Q6 15 8 13 Q10 10 11 8 Z" />
      
      {/* Right wing */}
      <path d="M13 6 Q16 8 18 12 Q19 14 20 16 L19 17 Q18 15 16 13 Q14 10 13 8 Z" />
      
      {/* Body center with gem */}
      <ellipse cx="12" cy="10" rx="2" ry="3" fill="currentColor" opacity="0.3" />
      <circle cx="12" cy="10" r="1" fill="currentColor" />
      
      {/* Tail flames - left */}
      <path d="M10 12 Q8 16 7 20 L8 21 Q9 18 10 14 Z" />
      
      {/* Tail flames - center */}
      <path d="M12 12 Q12 16 12 22" />
      
      {/* Tail flames - right */}
      <path d="M14 12 Q16 16 17 20 L16 21 Q15 18 14 14 Z" />
      
      {/* Wing details - left */}
      <path d="M9 9 L7 11" opacity="0.5" />
      <path d="M8 11 L6 14" opacity="0.5" />
      
      {/* Wing details - right */}
      <path d="M15 9 L17 11" opacity="0.5" />
      <path d="M16 11 L18 14" opacity="0.5" />
      
      {/* Top flames */}
      <path d="M11 4 Q10 2 9 1" opacity="0.6" />
      <path d="M13 4 Q14 2 15 1" opacity="0.6" />
    </svg>
  );
};

