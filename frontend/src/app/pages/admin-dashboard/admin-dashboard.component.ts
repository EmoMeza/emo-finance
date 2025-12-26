import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AdminService, UserResponse, UserCreate, UserUpdate, AdminStats } from '../../services/admin.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrl: './admin-dashboard.component.scss'
})
export class AdminDashboardComponent implements OnInit {
  private adminService = inject(AdminService);
  private fb = inject(FormBuilder);

  users = signal<UserResponse[]>([]);
  stats = signal<AdminStats | null>(null);
  loading = signal(false);
  error = signal<string | null>(null);

  showCreateModal = signal(false);
  showEditModal = signal(false);
  selectedUser = signal<UserResponse | null>(null);

  createUserForm: FormGroup;
  editUserForm: FormGroup;

  constructor() {
    this.createUserForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      username: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      first_name: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(100)]],
      last_name: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(100)]],
      password: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(100)]],
      role: ['user', Validators.required]
    });

    this.editUserForm = this.fb.group({
      email: ['', [Validators.email]],
      username: ['', [Validators.minLength(3), Validators.maxLength(50)]],
      first_name: ['', [Validators.minLength(1), Validators.maxLength(100)]],
      last_name: ['', [Validators.minLength(1), Validators.maxLength(100)]],
      password: ['', [Validators.minLength(8), Validators.maxLength(100)]],
      role: ['']
    });
  }

  ngOnInit(): void {
    this.loadUsers();
    this.loadStats();
  }

  loadUsers(): void {
    this.loading.set(true);
    this.error.set(null);

    this.adminService.getAllUsers().subscribe({
      next: (users) => {
        this.users.set(users);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Error al cargar usuarios');
        this.loading.set(false);
        console.error('Error loading users:', err);
      }
    });
  }

  loadStats(): void {
    this.adminService.getStats().subscribe({
      next: (stats) => {
        this.stats.set(stats);
      },
      error: (err) => {
        console.error('Error loading stats:', err);
      }
    });
  }

  openCreateModal(): void {
    this.createUserForm.reset({ role: 'user' });
    this.showCreateModal.set(true);
  }

  closeCreateModal(): void {
    this.showCreateModal.set(false);
    this.createUserForm.reset();
  }

  onCreateUser(): void {
    if (this.createUserForm.valid) {
      this.loading.set(true);
      this.error.set(null);

      const userData: UserCreate = this.createUserForm.value;

      this.adminService.createUser(userData).subscribe({
        next: () => {
          this.closeCreateModal();
          this.loadUsers();
          this.loadStats();
          this.loading.set(false);
        },
        error: (err) => {
          this.error.set(err.error?.detail || 'Error al crear usuario');
          this.loading.set(false);
          console.error('Error creating user:', err);
        }
      });
    }
  }

  openEditModal(user: UserResponse): void {
    this.selectedUser.set(user);
    this.editUserForm.patchValue({
      email: user.email,
      username: user.username,
      first_name: user.first_name,
      last_name: user.last_name,
      role: user.role,
      password: ''
    });
    this.showEditModal.set(true);
  }

  closeEditModal(): void {
    this.showEditModal.set(false);
    this.selectedUser.set(null);
    this.editUserForm.reset();
  }

  onEditUser(): void {
    const user = this.selectedUser();
    if (!user || !this.editUserForm.valid) return;

    this.loading.set(true);
    this.error.set(null);

    const userData: UserUpdate = {};
    const formValue = this.editUserForm.value;

    if (formValue.email && formValue.email !== user.email) {
      userData.email = formValue.email;
    }
    if (formValue.username && formValue.username !== user.username) {
      userData.username = formValue.username;
    }
    if (formValue.first_name && formValue.first_name !== user.first_name) {
      userData.first_name = formValue.first_name;
    }
    if (formValue.last_name && formValue.last_name !== user.last_name) {
      userData.last_name = formValue.last_name;
    }
    if (formValue.password) {
      userData.password = formValue.password;
    }
    if (formValue.role && formValue.role !== user.role) {
      userData.role = formValue.role;
    }

    this.adminService.updateUser(user._id, userData).subscribe({
      next: () => {
        this.closeEditModal();
        this.loadUsers();
        this.loadStats();
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Error al actualizar usuario');
        this.loading.set(false);
        console.error('Error updating user:', err);
      }
    });
  }

  onDeleteUser(user: UserResponse): void {
    if (!confirm(`¿Está seguro de que desea eliminar al usuario ${user.username}?`)) {
      return;
    }

    this.loading.set(true);
    this.error.set(null);

    this.adminService.deleteUser(user._id).subscribe({
      next: () => {
        this.loadUsers();
        this.loadStats();
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Error al eliminar usuario');
        this.loading.set(false);
        console.error('Error deleting user:', err);
      }
    });
  }
}
