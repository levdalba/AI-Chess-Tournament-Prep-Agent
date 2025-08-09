import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { Button, Input, Card, CardHeader, CardContent } from '../components/ui'
import { useRegister } from '../hooks/api'

interface RegisterForm {
    username: string
    email: string
    password: string
    confirmPassword: string
}

export function RegisterPage() {
    const navigate = useNavigate()
    const registerMutation = useRegister()

    const {
        register,
        handleSubmit,
        formState: { errors },
        watch,
    } = useForm<RegisterForm>()

    const onSubmit = async (data: RegisterForm) => {
        try {
            const result = await registerMutation.mutateAsync({
                username: data.username,
                email: data.email,
                password: data.password,
            })
            if (result.success) {
                navigate('/login')
            }
        } catch (error) {
            console.error('Registration failed:', error)
        }
    }

    const password = watch('password')

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div className="text-center">
                    <div className="mx-auto h-12 w-12 bg-chess-primary rounded-lg flex items-center justify-center">
                        <span className="text-white font-bold text-xl">♕</span>
                    </div>
                    <h2 className="mt-6 text-3xl font-bold text-gray-900">
                        Create your account
                    </h2>
                    <p className="mt-2 text-sm text-gray-600">
                        Already have an account?{' '}
                        <Link
                            to="/login"
                            className="font-medium text-chess-primary hover:text-chess-primary/80"
                        >
                            Sign in here
                        </Link>
                    </p>
                </div>

                <Card>
                    <CardHeader>
                        <h3 className="text-lg font-medium">
                            Get started today
                        </h3>
                    </CardHeader>
                    <CardContent>
                        <form
                            onSubmit={handleSubmit(onSubmit)}
                            className="space-y-4"
                        >
                            <Input
                                label="Username"
                                type="text"
                                autoComplete="username"
                                error={errors.username?.message}
                                {...register('username', {
                                    required: 'Username is required',
                                    minLength: {
                                        value: 3,
                                        message:
                                            'Username must be at least 3 characters',
                                    },
                                })}
                            />

                            <Input
                                label="Email address"
                                type="email"
                                autoComplete="email"
                                error={errors.email?.message}
                                {...register('email', {
                                    required: 'Email is required',
                                    pattern: {
                                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                        message: 'Invalid email address',
                                    },
                                })}
                            />

                            <Input
                                label="Password"
                                type="password"
                                autoComplete="new-password"
                                error={errors.password?.message}
                                {...register('password', {
                                    required: 'Password is required',
                                    minLength: {
                                        value: 8,
                                        message:
                                            'Password must be at least 8 characters',
                                    },
                                })}
                            />

                            <Input
                                label="Confirm Password"
                                type="password"
                                autoComplete="new-password"
                                error={errors.confirmPassword?.message}
                                {...register('confirmPassword', {
                                    required: 'Please confirm your password',
                                    validate: (value) =>
                                        value === password ||
                                        'The passwords do not match',
                                })}
                            />

                            <Button
                                type="submit"
                                className="w-full"
                                loading={registerMutation.isPending}
                            >
                                Create Account
                            </Button>
                        </form>
                    </CardContent>
                </Card>

                <div className="text-center">
                    <Link
                        to="/"
                        className="text-chess-primary hover:text-chess-primary/80"
                    >
                        ← Back to home
                    </Link>
                </div>
            </div>
        </div>
    )
}
