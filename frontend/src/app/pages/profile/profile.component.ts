import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ProfileService, UpdateProfileRequest, ChangePasswordRequest } from '../../services/profile.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent {
  private fb = inject(FormBuilder);
  private router = inject(Router);
  private profileService = inject(ProfileService);
  public authService = inject(AuthService);

  showEditModal = signal(false);
  showPasswordModal = signal(false);
  loading = signal(false);
  error = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  editProfileForm: FormGroup;
  changePasswordForm: FormGroup;

  constructor() {
    const user = this.authService.currentUser();

    this.editProfileForm = this.fb.group({
      email: [user?.email || '', [Validators.required, Validators.email]],
      username: [user?.username || '', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      first_name: [user?.first_name || '', [Validators.required, Validators.minLength(1), Validators.maxLength(100)]],
      last_name: [user?.last_name || '', [Validators.required, Validators.minLength(1), Validators.maxLength(100)]]
    });

    this.changePasswordForm = this.fb.group({
      current_password: ['', [Validators.required]],
      new_password: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(100)]],
      confirm_password: ['', [Validators.required]]
    });
  }

  openEditModal(): void {
    const user = this.authService.currentUser();
    this.editProfileForm.patchValue({
      email: user?.email,
      username: user?.username,
      first_name: user?.first_name,
      last_name: user?.last_name
    });
    this.error.set(null);
    this.successMessage.set(null);
    this.showEditModal.set(true);
  }

  closeEditModal(): void {
    this.showEditModal.set(false);
    this.editProfileForm.reset();
  }

  openPasswordModal(): void {
    this.changePasswordForm.reset();
    this.error.set(null);
    this.successMessage.set(null);
    this.showPasswordModal.set(true);
  }

  closePasswordModal(): void {
    this.showPasswordModal.set(false);
    this.changePasswordForm.reset();
  }

  onUpdateProfile(): void {
    if (this.editProfileForm.valid) {
      this.loading.set(true);
      this.error.set(null);

      const profileData: UpdateProfileRequest = {};
      const formValue = this.editProfileForm.value;
      const user = this.authService.currentUser();

      if (formValue.email && formValue.email !== user?.email) {
        profileData.email = formValue.email;
      }
      if (formValue.username && formValue.username !== user?.username) {
        profileData.username = formValue.username;
      }
      if (formValue.first_name && formValue.first_name !== user?.first_name) {
        profileData.first_name = formValue.first_name;
      }
      if (formValue.last_name && formValue.last_name !== user?.last_name) {
        profileData.last_name = formValue.last_name;
      }

      // If nothing changed, just close the modal
      if (Object.keys(profileData).length === 0) {
        this.closeEditModal();
        this.loading.set(false);
        return;
      }

      this.profileService.updateProfile(profileData).subscribe({
        next: (updatedUser) => {
          // Update the user in AuthService
          this.authService.loadCurrentUser();
          this.successMessage.set('Perfil actualizado exitosamente');
          this.loading.set(false);
          setTimeout(() => {
            this.closeEditModal();
            this.successMessage.set(null);
          }, 2000);
        },
        error: (err) => {
          this.error.set(err.error?.detail || 'Error al actualizar perfil');
          this.loading.set(false);
        }
      });
    }
  }

  onChangePassword(): void {
    if (this.changePasswordForm.valid) {
      const currentPassword = this.changePasswordForm.get('current_password')?.value;
      const newPassword = this.changePasswordForm.get('new_password')?.value;
      const confirmPassword = this.changePasswordForm.get('confirm_password')?.value;

      if (newPassword !== confirmPassword) {
        this.error.set('Las contraseñas no coinciden');
        return;
      }

      this.loading.set(true);
      this.error.set(null);

      const passwordData: ChangePasswordRequest = {
        current_password: currentPassword,
        new_password: newPassword
      };

      this.profileService.changePassword(passwordData).subscribe({
        next: (response) => {
          this.successMessage.set(response.message);
          this.loading.set(false);
          setTimeout(() => {
            this.closePasswordModal();
            this.successMessage.set(null);
          }, 2000);
        },
        error: (err) => {
          this.error.set(err.error?.detail || 'Error al cambiar contraseña');
          this.loading.set(false);
        }
      });
    }
  }

  onDeleteAccount(): void {
    const user = this.authService.currentUser();
    if (!user) return;

    const confirmed = confirm(
      '¿Estás seguro de que deseas eliminar tu cuenta? Esta acción no se puede deshacer.'
    );

    if (!confirmed) return;

    this.loading.set(true);
    this.error.set(null);

    this.profileService.deleteAccount(user._id).subscribe({
      next: () => {
        this.authService.logout();
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Error al eliminar cuenta');
        this.loading.set(false);
      }
    });
  }
}
