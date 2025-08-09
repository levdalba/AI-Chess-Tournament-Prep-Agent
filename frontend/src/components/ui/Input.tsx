import React from 'react'
import { cn } from '../../utils/cn'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string
    error?: string
    helperText?: string
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
    (
        { className, type = 'text', label, error, helperText, id, ...props },
        ref
    ) => {
        const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`

        return (
            <div className="space-y-2">
                {label && (
                    <label
                        htmlFor={inputId}
                        className="block text-sm font-medium text-gray-700"
                    >
                        {label}
                    </label>
                )}
                <input
                    type={type}
                    className={cn(
                        'block w-full rounded-lg border-gray-300 shadow-sm focus:border-chess-primary focus:ring focus:ring-chess-primary/20 transition-colors duration-200',
                        error &&
                            'border-red-300 focus:border-red-500 focus:ring-red-200',
                        className
                    )}
                    ref={ref}
                    id={inputId}
                    {...props}
                />
                {error && <p className="text-sm text-red-600">{error}</p>}
                {helperText && !error && (
                    <p className="text-sm text-gray-500">{helperText}</p>
                )}
            </div>
        )
    }
)

Input.displayName = 'Input'
