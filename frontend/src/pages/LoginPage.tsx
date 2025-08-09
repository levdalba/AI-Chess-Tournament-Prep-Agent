import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { Button, Input, Card, CardHeader, CardContent } from '../components/ui'
import { useLogin } from '../hooks/api'

interface LoginForm {
    email: string
    password: string
}

export function LoginPage() {
    const navigate = useNavigate()
    const loginMutation = useLogin()

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginForm>()

    const onSubmit = async (data: LoginForm) => {
        try {
            const result = await loginMutation.mutateAsync(data)
            if (result.success) {
                navigate('/dashboard')
            }
        } catch (error) {
            console.error('Login failed:', error)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div className="text-center">
                    <div className="mx-auto h-12 w-12 bg-chess-primary rounded-lg flex items-center justify-center">
                        <span className="text-white font-bold text-xl">♕</span>
                    </div>
                    <h2 className="mt-6 text-3xl font-bold text-gray-900">
                        Sign in to your account
                    </h2>
                    <p className="mt-2 text-sm text-gray-600">
                        Don't have an account?{' '}
                        <Link
                            to="/register"
                            className="font-medium text-chess-primary hover:text-chess-primary/80"
                        >
                            Sign up here
                        </Link>
                    </p>
                </div>

                <Card>
                    <CardHeader>
                        <h3 className="text-lg font-medium">Welcome back</h3>
                    </CardHeader>
                    <CardContent>
                        <form
                            onSubmit={handleSubmit(onSubmit)}
                            className="space-y-4"
                        >
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
                                autoComplete="current-password"
                                error={errors.password?.message}
                                {...register('password', {
                                    required: 'Password is required',
                                    minLength: {
                                        value: 6,
                                        message:
                                            'Password must be at least 6 characters',
                                    },
                                })}
                            />

                            <Button
                                type="submit"
                                className="w-full"
                                loading={loginMutation.isPending}
                            >
                                Sign In
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
