import { Injectable, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { MetodoPago } from './expense.service';
import { environment } from '../../../environments/environment';

export interface ExpenseTemplate {
  _id: string;
  user_id: string;
  nombre: string;
  valor: number;
  categoria_id: string;
  subcategoria_nombre?: string;
  dia_cargo: number;
  metodo_pago: MetodoPago;
  activa: boolean;
  notas?: string;
  created_at: string;
  updated_at: string;
}

export interface ExpenseTemplateCreate {
  nombre: string;
  valor: number;
  categoria_id: string;
  subcategoria_nombre?: string;
  dia_cargo: number;
  metodo_pago: MetodoPago;
  activa?: boolean;
  notas?: string;
}

export interface ExpenseTemplateUpdate {
  nombre?: string;
  valor?: number;
  subcategoria_nombre?: string;
  dia_cargo?: number;
  metodo_pago?: MetodoPago;
  activa?: boolean;
  notas?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ExpenseTemplateService {
  private readonly API_URL = environment.apiUrl;

  // Signals
  templates = signal<ExpenseTemplate[]>([]);
  activeTemplates = signal<ExpenseTemplate[]>([]);

  constructor(private http: HttpClient) {}

  createTemplate(templateData: ExpenseTemplateCreate): Observable<ExpenseTemplate> {
    return this.http.post<ExpenseTemplate>(`${this.API_URL}/expense-templates/`, templateData);
  }

  getTemplates(activa?: boolean): Observable<ExpenseTemplate[]> {
    let params = new HttpParams();
    if (activa !== undefined) {
      params = params.set('activa', activa.toString());
    }

    return this.http.get<ExpenseTemplate[]>(`${this.API_URL}/expense-templates/`, { params }).pipe(
      tap(templates => {
        this.templates.set(templates);
        if (activa === true || activa === undefined) {
          this.activeTemplates.set(templates.filter(t => t.activa));
        }
      })
    );
  }

  getTemplateById(templateId: string): Observable<ExpenseTemplate> {
    return this.http.get<ExpenseTemplate>(`${this.API_URL}/expense-templates/${templateId}`);
  }

  updateTemplate(templateId: string, updateData: ExpenseTemplateUpdate): Observable<ExpenseTemplate> {
    return this.http.put<ExpenseTemplate>(`${this.API_URL}/expense-templates/${templateId}`, updateData);
  }

  toggleTemplate(templateId: string): Observable<ExpenseTemplate> {
    return this.http.patch<ExpenseTemplate>(`${this.API_URL}/expense-templates/${templateId}/toggle`, {});
  }

  deleteTemplate(templateId: string): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/expense-templates/${templateId}`);
  }

  // Helper para calcular total mensual de plantillas activas
  calculateMonthlyTotal(templates: ExpenseTemplate[]): number {
    return templates
      .filter(t => t.activa)
      .reduce((sum, t) => sum + t.valor, 0);
  }
}
