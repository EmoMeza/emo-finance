import { Injectable, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { Expense, ExpenseCreate, ExpenseUpdate, TipoGasto } from '../models';

@Injectable({
  providedIn: 'root'
})
export class ExpenseService {
  private readonly API_URL = `${environment.apiUrl}/expenses`;

  // Signal for reactive expenses state
  expenses = signal<Expense[]>([]);
  isLoading = signal<boolean>(false);

  constructor(private http: HttpClient) {}

  /**
   * Obtener todos los gastos de un período
   */
  getExpenses(
    periodoId: string,
    tipo?: TipoGasto,
    categoriaId?: string
  ): Observable<Expense[]> {
    this.isLoading.set(true);

    let params = new HttpParams().set('periodo_id', periodoId);

    if (tipo) {
      params = params.set('tipo', tipo);
    }

    if (categoriaId) {
      params = params.set('categoria_id', categoriaId);
    }

    return this.http.get<Expense[]>(this.API_URL, { params }).pipe(
      tap(expenses => {
        this.expenses.set(expenses);
        this.isLoading.set(false);
      })
    );
  }

  /**
   * Obtener un gasto por ID
   */
  getExpenseById(id: string): Observable<Expense> {
    return this.http.get<Expense>(`${this.API_URL}/${id}`);
  }

  /**
   * Crear un nuevo gasto
   */
  createExpense(periodoId: string, expense: ExpenseCreate): Observable<Expense> {
    const params = new HttpParams().set('periodo_id', periodoId);

    return this.http.post<Expense>(this.API_URL, expense, { params }).pipe(
      tap(newExpense => {
        this.expenses.update(exps => [...exps, newExpense]);
      })
    );
  }

  /**
   * Actualizar un gasto
   */
  updateExpense(id: string, updates: ExpenseUpdate): Observable<Expense> {
    return this.http.put<Expense>(`${this.API_URL}/${id}`, updates).pipe(
      tap(updatedExpense => {
        this.expenses.update(exps =>
          exps.map(exp => exp._id === id ? updatedExpense : exp)
        );
      })
    );
  }

  /**
   * Eliminar un gasto
   */
  deleteExpense(id: string): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/${id}`).pipe(
      tap(() => {
        this.expenses.update(exps => exps.filter(exp => exp._id !== id));
      })
    );
  }

  /**
   * Obtener gastos fijos de un período
   */
  getGastosFijos(periodoId: string, categoriaId?: string): Observable<Expense[]> {
    return this.getExpenses(periodoId, TipoGasto.FIJO, categoriaId);
  }

  /**
   * Obtener gastos variables de un período
   */
  getGastosVariables(periodoId: string, categoriaId?: string): Observable<Expense[]> {
    return this.getExpenses(periodoId, TipoGasto.VARIABLE, categoriaId);
  }

  /**
   * Obtener gastos fijos permanentes (se copian cada período)
   */
  getGastosFijosPermanentes(): Expense[] {
    return this.expenses().filter(exp =>
      exp.tipo === TipoGasto.FIJO && exp.es_permanente === true
    );
  }

  /**
   * Obtener gastos fijos temporales (cuotas)
   */
  getGastosFijosTemporales(): Expense[] {
    return this.expenses().filter(exp =>
      exp.tipo === TipoGasto.FIJO &&
      exp.es_permanente === false &&
      (exp.periodos_restantes ?? 0) > 0
    );
  }

  /**
   * Calcular total de gastos de una categoría
   */
  getTotalByCategoria(categoriaId: string): number {
    return this.expenses()
      .filter(exp => exp.categoria_id === categoriaId)
      .reduce((sum, exp) => sum + exp.monto, 0);
  }

  /**
   * Calcular total de todos los gastos
   */
  getTotal(): number {
    return this.expenses().reduce((sum, exp) => sum + exp.monto, 0);
  }
}
