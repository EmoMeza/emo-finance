import { Injectable, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

export enum TipoGasto {
  FIJO = 'fijo',
  VARIABLE = 'variable'
}

export enum EstadoGasto {
  PENDIENTE = 'pendiente',
  PAGADO = 'pagado',
  PROYECTADO = 'proyectado'
}

export enum MetodoPago {
  CREDITO = 'credito',
  DEBITO = 'debito',
  EFECTIVO = 'efectivo',
  TRANSFERENCIA = 'transferencia'
}

export interface Expense {
  _id: string;
  user_id: string;
  periodo_id: string;
  plantilla_id?: string;
  nombre: string;
  valor: number;
  fecha: string;
  categoria_id: string;
  subcategoria_nombre?: string;
  tipo: TipoGasto;
  metodo_pago: MetodoPago;
  estado: EstadoGasto;
  notas?: string;
  created_at: string;
  updated_at: string;
}

export interface ExpenseCreate {
  periodo_id: string;
  plantilla_id?: string;
  nombre: string;
  valor: number;
  fecha: string;
  categoria_id: string;
  subcategoria_nombre?: string;
  tipo: TipoGasto;
  metodo_pago: MetodoPago;
  estado?: EstadoGasto;
  notas?: string;
}

export interface ExpenseUpdate {
  nombre?: string;
  valor?: number;
  fecha?: string;
  subcategoria_nombre?: string;
  metodo_pago?: MetodoPago;
  estado?: EstadoGasto;
  notas?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ExpenseService {
  private readonly API_URL = 'http://localhost:8000/api/v1';

  // Signals
  expenses = signal<Expense[]>([]);

  constructor(private http: HttpClient) {}

  createExpense(expenseData: ExpenseCreate): Observable<Expense> {
    return this.http.post<Expense>(`${this.API_URL}/expenses/`, expenseData);
  }

  getExpenses(
    periodoId?: string,
    categoriaId?: string,
    tipo?: TipoGasto,
    estado?: EstadoGasto
  ): Observable<Expense[]> {
    let params = new HttpParams();

    if (periodoId) {
      params = params.set('periodo_id', periodoId);
    }
    if (categoriaId) {
      params = params.set('categoria_id', categoriaId);
    }
    if (tipo) {
      params = params.set('tipo', tipo);
    }
    if (estado) {
      params = params.set('estado', estado);
    }

    return this.http.get<Expense[]>(`${this.API_URL}/expenses/`, { params }).pipe(
      tap(expenses => this.expenses.set(expenses))
    );
  }

  getExpenseById(expenseId: string): Observable<Expense> {
    return this.http.get<Expense>(`${this.API_URL}/expenses/${expenseId}`);
  }

  updateExpense(expenseId: string, updateData: ExpenseUpdate): Observable<Expense> {
    return this.http.put<Expense>(`${this.API_URL}/expenses/${expenseId}`, updateData);
  }

  markAsPaid(expenseId: string): Observable<Expense> {
    return this.http.patch<Expense>(`${this.API_URL}/expenses/${expenseId}/mark-paid`, {});
  }

  deleteExpense(expenseId: string): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/expenses/${expenseId}`);
  }

  // Método helper para calcular total
  calculateTotal(expenses: Expense[]): number {
    return expenses.reduce((sum, exp) => sum + exp.valor, 0);
  }

  // Filtrar por categoría
  filterByCategory(expenses: Expense[], categoriaId: string): Expense[] {
    return expenses.filter(exp => exp.categoria_id === categoriaId);
  }
}
