import React from 'react';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: 'default' | 'destructive';
}

export const Alert: React.FC<AlertProps> = ({ 
  children, 
  variant = 'default', 
  className = '', 
  ...props 
}) => {
  const variantClasses = {
    default: 'bg-blue-50 border-blue-200 text-blue-800',
    destructive: 'bg-red-50 border-red-200 text-red-800'
  };

  return (
    <div 
      className={`rounded-lg border p-4 ${variantClasses[variant]} ${className}`} 
      {...props}
    >
      {children}
    </div>
  );
};

export const AlertTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ 
  children, 
  className = '', 
  ...props 
}) => {
  return (
    <h5 className={`mb-1 font-medium leading-none tracking-tight ${className}`} {...props}>
      {children}
    </h5>
  );
};

export const AlertDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({ 
  children, 
  className = '', 
  ...props 
}) => {
  return (
    <div className={`text-sm opacity-90 ${className}`} {...props}>
      {children}
    </div>
  );
};