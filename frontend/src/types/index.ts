// Shared types (mirrored from shared/models.py)
export const GameResult = {
    WHITE_WIN: '1-0',
    BLACK_WIN: '0-1',
    DRAW: '1/2-1/2',
    UNKNOWN: '*',
} as const

export type GameResult = (typeof GameResult)[keyof typeof GameResult]

export interface TimeControl {
    base_time: number // seconds
    increment: number // seconds per move
}

export interface Player {
    name: string
    rating?: number
    title?: string
}

export interface GameMetadata {
    event?: string
    site?: string
    date?: string
    round?: string
    white?: Player
    black?: Player
    result: GameResult
    eco?: string // Encyclopedia of Chess Openings
    time_control?: TimeControl
}

export interface Move {
    move_number: number
    white_move?: string
    black_move?: string
    white_time?: number // time left after move
    black_time?: number
    white_eval?: number // centipawn evaluation
    black_eval?: number
}

export interface Game {
    id?: string
    metadata: GameMetadata
    moves: Move[]
    pgn: string
    created_at?: string
}

export interface Opening {
    eco_code: string
    name: string
    moves: string
    frequency: number // how often opponent plays this
}

export interface WeakPoint {
    position_fen: string
    move: string
    eval_before: number
    eval_after: number
    eval_loss: number // centipawns lost
    move_number: number
    phase: string // opening, middlegame, endgame
}

export interface PrepPlan {
    id?: string
    opponent_name: string
    tournament_date?: string
    common_openings: Opening[]
    weak_points: WeakPoint[]
    recommendations: string // AI-generated recommendations
    daily_drills: string[]
    created_at?: string
}

export interface User {
    id?: string
    email: string
    username: string
    rating?: number
    created_at?: string
    is_active: boolean
}

// Frontend-specific types
export interface ApiResponse<T = any> {
    success: boolean
    data?: T
    error?: string
    message?: string
}

export interface PaginatedResponse<T> {
    items: T[]
    total: number
    page: number
    size: number
    pages: number
}

export interface UploadProgress {
    loaded: number
    total: number
    percent: number
}

export interface GameAnalysisResult {
    totalGames: number
    commonOpenings: Opening[]
    weakPoints: WeakPoint[]
    averageRating?: number
    timeControls: TimeControl[]
    analysisDate: string
}

export interface PrepPlanRequest {
    opponentName: string
    tournamentDate?: string
    gameIds: string[]
    preferences?: {
        focusAreas?: string[]
        difficultyLevel?: 'beginner' | 'intermediate' | 'advanced'
        prepDays?: number
    }
}

export interface DailyDrill {
    id: string
    date: string
    title: string
    description: string
    category: 'tactics' | 'opening' | 'endgame' | 'strategy'
    difficulty: 1 | 2 | 3 | 4 | 5
    completed: boolean
    puzzleData?: {
        fen: string
        solution: string[]
        explanation: string
    }
}

export interface UserProfile {
    id: string
    username: string
    email: string
    rating?: number
    preferredTimeControl?: string
    memberSince: string
    totalAnalyses: number
    totalPrepPlans: number
}

export interface NotificationSettings {
    dailyDrills: boolean
    gameAnalysis: boolean
    prepPlanUpdates: boolean
    email: boolean
    push: boolean
}
