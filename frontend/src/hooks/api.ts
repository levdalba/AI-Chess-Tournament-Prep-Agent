import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type {
  PrepPlan,
  PrepPlanRequest,
  UserProfile,
} from '../types'

// Query Keys
export const queryKeys = {
    games: ['games'] as const,
    gamesPage: (page: number, size: number) => ['games', page, size] as const,
    analysis: (analysisId: string) => ['analysis', analysisId] as const,
    prepPlans: ['prepPlans'] as const,
    prepPlan: (id: string) => ['prepPlan', id] as const,
    dailyDrills: (date?: string) => ['dailyDrills', date] as const,
    profile: ['profile'] as const,
    health: ['health'] as const,
}

// Auth Hooks
export function useLogin() {
    return useMutation({
        mutationFn: ({
            email,
            password,
        }: {
            email: string
            password: string
        }) => apiClient.login(email, password),
        onSuccess: (data) => {
            if (data.success && data.data?.access_token) {
                localStorage.setItem('auth_token', data.data.access_token)
            }
        },
    })
}

export function useRegister() {
    return useMutation({
        mutationFn: ({
            email,
            username,
            password,
        }: {
            email: string
            username: string
            password: string
        }) => apiClient.register(email, username, password),
    })
}

export function useLogout() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: () => apiClient.logout(),
        onSuccess: () => {
            queryClient.clear()
        },
    })
}

// User Profile Hooks
export function useProfile() {
    return useQuery({
        queryKey: queryKeys.profile,
        queryFn: () => apiClient.getProfile(),
        enabled: !!localStorage.getItem('auth_token'),
    })
}

export function useUpdateProfile() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (updates: Partial<UserProfile>) =>
            apiClient.updateProfile(updates),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.profile })
        },
    })
}

// Games and Upload Hooks
export function useGames(page = 1, size = 50) {
    return useQuery({
        queryKey: queryKeys.gamesPage(page, size),
        queryFn: () => apiClient.getGames(page, size),
    })
}

export function useUploadPgn() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({
            file,
            onProgress,
        }: {
            file: File
            onProgress?: (progress: number) => void
        }) => apiClient.uploadPgn(file, onProgress),
        onSuccess: () => {
            // Invalidate games queries to refresh the list
            queryClient.invalidateQueries({ queryKey: queryKeys.games })
        },
    })
}

// Analysis Hooks
export function useAnalyzeGames() {
    return useMutation({
        mutationFn: (gameIds: string[]) => apiClient.analyzeGames(gameIds),
    })
}

export function useAnalysisResult(analysisId: string, enabled = true) {
    return useQuery({
        queryKey: queryKeys.analysis(analysisId),
        queryFn: () => apiClient.getAnalysisResult(analysisId),
        enabled,
    })
}

// Prep Plan Hooks
export function usePrepPlans() {
    return useQuery({
        queryKey: queryKeys.prepPlans,
        queryFn: () => apiClient.getPrepPlans(),
    })
}

export function usePrepPlan(id: string) {
    return useQuery({
        queryKey: queryKeys.prepPlan(id),
        queryFn: () => apiClient.getPrepPlan(id),
        enabled: !!id,
    })
}

export function useCreatePrepPlan() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (request: PrepPlanRequest) =>
            apiClient.createPrepPlan(request),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.prepPlans })
        },
    })
}

export function useUpdatePrepPlan() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({
            id,
            updates,
        }: {
            id: string
            updates: Partial<PrepPlan>
        }) => apiClient.updatePrepPlan(id, updates),
        onSuccess: (_, { id }) => {
            queryClient.invalidateQueries({ queryKey: queryKeys.prepPlan(id) })
            queryClient.invalidateQueries({ queryKey: queryKeys.prepPlans })
        },
    })
}

export function useDeletePrepPlan() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => apiClient.deletePrepPlan(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.prepPlans })
        },
    })
}

// Daily Drills Hooks
export function useDailyDrills(date?: string) {
    return useQuery({
        queryKey: queryKeys.dailyDrills(date),
        queryFn: () => apiClient.getDailyDrills(date),
    })
}

export function useCompleteDrill() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (drillId: string) => apiClient.completeDrill(drillId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.dailyDrills() })
        },
    })
}

// Health Check Hook
export function useHealthCheck() {
    return useQuery({
        queryKey: queryKeys.health,
        queryFn: () => apiClient.healthCheck(),
        refetchInterval: 30000, // Check every 30 seconds
    })
}
