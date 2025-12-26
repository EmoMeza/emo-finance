import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface UserCreate {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  password: string;
  role: 'admin' | 'user';
}

export interface UserUpdate {
  email?: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  password?: string;
  role?: 'admin' | 'user';
}

export interface UserResponse {
  _id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AdminStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  admin_users: number;
  regular_users: number;
}

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/admin`;

  /**
   * Get all users in the system
   */
  getAllUsers(skip: number = 0, limit: number = 100): Observable<UserResponse[]> {
    return this.http.get<UserResponse[]>(`${this.apiUrl}/users`, {
      params: { skip: skip.toString(), limit: limit.toString() }
    });
  }

  /**
   * Create a new user (admin only)
   */
  createUser(userData: UserCreate): Observable<UserResponse> {
    return this.http.post<UserResponse>(`${this.apiUrl}/users`, userData);
  }

  /**
   * Update a user by ID (admin only)
   */
  updateUser(userId: string, userData: UserUpdate): Observable<UserResponse> {
    return this.http.put<UserResponse>(`${this.apiUrl}/users/${userId}`, userData);
  }

  /**
   * Delete a user by ID (admin only)
   */
  deleteUser(userId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/users/${userId}`);
  }

  /**
   * Get system statistics (admin only)
   */
  getStats(): Observable<AdminStats> {
    return this.http.get<AdminStats>(`${this.apiUrl}/stats`);
  }
}
