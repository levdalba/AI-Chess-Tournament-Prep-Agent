import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'
import type {
    ApiResponse,
    PaginatedResponse,
    Game,
    GameAnalysisResult,
    PrepPlan,
    PrepPlanRequest,
    DailyDrill,
    UserProfile,
    User,
} from '../types'

class ApiClient {
    private client: AxiosInstance

    constructor() {
        this.client = axios.create({
            baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
            },
        })

        // Request interceptor for auth tokens
        this.client.interceptors.request.use(
            (config) => {
                const token = localStorage.getItem('auth_token')
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`
                }
                return config
            },
            (error) => Promise.reject(error)
        )

        // Response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            (error) => {
                if (error.response?.status === 401) {
                    // Handle unauthorized - redirect to login
                    localStorage.removeItem('auth_token')
                    window.location.href = '/login'
                }
                return Promise.reject(error)
            }
        )
    }

    // Authentication
    async login(
        email: string,
        password: string
    ): Promise<ApiResponse<{ access_token: string; user: User }>> {
        const response: AxiosResponse<
            ApiResponse<{ access_token: string; user: User }>
        > = await this.client.post('/auth/login', { email, password })
        return response.data
    }

    async register(
        email: string,
        username: string,
        password: string
    ): Promise<ApiResponse<User>> {
        const response: AxiosResponse<ApiResponse<User>> =
            await this.client.post('/auth/register', {
                email,
                username,
                password,
            })
        return response.data
    }

    async logout(): Promise<void> {
        await this.client.post('/auth/logout')
        localStorage.removeItem('auth_token')
    }

    // User Profile
    async getProfile(): Promise<ApiResponse<UserProfile>> {
        const response: AxiosResponse<ApiResponse<UserProfile>> =
            await this.client.get('/users/me')
        return response.data
    }

    async updateProfile(
        updates: Partial<UserProfile>
    ): Promise<ApiResponse<UserProfile>> {
        const response: AxiosResponse<ApiResponse<UserProfile>> =
            await this.client.patch('/users/me', updates)
        return response.data
    }

    // PGN Upload and Analysis
    async uploadPgn(
        file: File,
        onProgress?: (progress: number) => void
    ): Promise<ApiResponse<{ uploadId: string; gameCount: number }>> {
        const formData = new FormData()
        formData.append('pgn_file', file)

        const response: AxiosResponse<
            ApiResponse<{ uploadId: string; gameCount: number }>
        > = await this.client.post('/games/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            onUploadProgress: (progressEvent) => {
                if (onProgress && progressEvent.total) {
                    const percent = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    )
                    onProgress(percent)
                }
            },
        })

        return response.data
    }

    async getGames(
        page = 1,
        size = 50
    ): Promise<ApiResponse<PaginatedResponse<Game>>> {
        const response: AxiosResponse<ApiResponse<PaginatedResponse<Game>>> =
            await this.client.get(`/games?page=${page}&size=${size}`)
        return response.data
    }

    async analyzeGames(
        gameIds: string[]
    ): Promise<ApiResponse<GameAnalysisResult>> {
        const response: AxiosResponse<ApiResponse<GameAnalysisResult>> =
            await this.client.post('/analysis/games', { game_ids: gameIds })
        return response.data
    }

    async getAnalysisResult(
        analysisId: string
    ): Promise<ApiResponse<GameAnalysisResult>> {
        const response: AxiosResponse<ApiResponse<GameAnalysisResult>> =
            await this.client.get(`/analysis/${analysisId}`)
        return response.data
    }

    // Prep Plans
    async createPrepPlan(
        request: PrepPlanRequest
    ): Promise<ApiResponse<PrepPlan>> {
        const response: AxiosResponse<ApiResponse<PrepPlan>> =
            await this.client.post('/prep-plans', request)
        return response.data
    }

    async getPrepPlans(): Promise<ApiResponse<PrepPlan[]>> {
        const response: AxiosResponse<ApiResponse<PrepPlan[]>> =
            await this.client.get('/prep-plans')
        return response.data
    }

    async getPrepPlan(id: string): Promise<ApiResponse<PrepPlan>> {
        const response: AxiosResponse<ApiResponse<PrepPlan>> =
            await this.client.get(`/prep-plans/${id}`)
        return response.data
    }

    async updatePrepPlan(
        id: string,
        updates: Partial<PrepPlan>
    ): Promise<ApiResponse<PrepPlan>> {
        const response: AxiosResponse<ApiResponse<PrepPlan>> =
            await this.client.patch(`/prep-plans/${id}`, updates)
        return response.data
    }

    async deletePrepPlan(id: string): Promise<ApiResponse<void>> {
        const response: AxiosResponse<ApiResponse<void>> =
            await this.client.delete(`/prep-plans/${id}`)
        return response.data
    }

    // Daily Drills
    async getDailyDrills(date?: string): Promise<ApiResponse<DailyDrill[]>> {
        const params = date ? `?date=${date}` : ''
        const response: AxiosResponse<ApiResponse<DailyDrill[]>> =
            await this.client.get(`/drills/daily${params}`)
        return response.data
    }

    async completeDrill(drillId: string): Promise<ApiResponse<void>> {
        const response: AxiosResponse<ApiResponse<void>> =
            await this.client.post(`/drills/${drillId}/complete`)
        return response.data
    }

    // Health Check
    async healthCheck(): Promise<
        ApiResponse<{ status: string; timestamp: string }>
    > {
        const response: AxiosResponse<
            ApiResponse<{ status: string; timestamp: string }>
        > = await this.client.get('/health')
        return response.data
    }
}

// Export a singleton instance
export const apiClient = new ApiClient()
export default apiClient
