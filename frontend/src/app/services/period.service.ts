import { Injectable, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  Period,
  PeriodCreate,
  PeriodUpdate,
  PeriodSummary,
  TipoPeriodo,
  EstadoPeriodo
} from '../models';

@Injectable({
  providedIn: 'root'
})
export class PeriodService {
  private readonly API_URL = `${environment.apiUrl}/periods/`;

  // Signals for reactive periods state
  periods = signal<Period[]>([]);
  activeMensualPeriod = signal<Period | null>(null);
  activeCreditPeriod = signal<Period | null>(null);
  currentSummary = signal<PeriodSummary | null>(null);
  isLoading = signal<boolean>(false);

  constructor(private http: HttpClient) {}

  /**
   * Obtener el período activo de un tipo específico
   * Si no existe, se crea automáticamente
   */
  getActivePeriod(tipoPeriodo: TipoPeriodo): Observable<Period> {
    this.isLoading.set(true);

    const params = new HttpParams().set('tipo_periodo', tipoPeriodo);

    return this.http.get<Period>(`${this.API_URL}active`, { params }).pipe(
      tap(period => {
        if (tipoPeriodo === TipoPeriodo.MENSUAL_ESTANDAR) {
          this.activeMensualPeriod.set(period);
        } else {
          this.activeCreditPeriod.set(period);
        }
        this.isLoading.set(false);
      })
    );
  }

  /**
   * Obtener todos los períodos con filtros opcionales
   */
  getPeriods(
    tipoPeriodo?: TipoPeriodo,
    estado?: EstadoPeriodo
  ): Observable<Period[]> {
    this.isLoading.set(true);

    let params = new HttpParams();

    if (tipoPeriodo) {
      params = params.set('tipo_periodo', tipoPeriodo);
    }

    if (estado) {
      params = params.set('estado', estado);
    }

    return this.http.get<Period[]>(this.API_URL, { params }).pipe(
      tap(periods => {
        this.periods.set(periods);
        this.isLoading.set(false);
      })
    );
  }

  /**
   * Obtener un período por ID
   */
  getPeriodById(id: string): Observable<Period> {
    return this.http.get<Period>(`${this.API_URL}${id}`);
  }

  /**
   * Obtener resumen completo del período con todas las categorías
   */
  getPeriodSummary(id: string): Observable<PeriodSummary> {
    this.isLoading.set(true);

    return this.http.get<PeriodSummary>(`${this.API_URL}${id}/summary`).pipe(
      tap(summary => {
        console.log('DEBUG: PeriodSummary recibido del backend:', summary);
        console.log('DEBUG: categories_summary:', summary.categories_summary);
        this.currentSummary.set(summary);
        this.isLoading.set(false);
      })
    );
  }

  /**
   * Crear un nuevo período manualmente
   */
  createPeriod(period: PeriodCreate): Observable<Period> {
    return this.http.post<Period>(this.API_URL, period).pipe(
      tap(newPeriod => {
        this.periods.update(pers => [...pers, newPeriod]);
      })
    );
  }

  /**
   * Actualizar un período
   */
  updatePeriod(id: string, updates: PeriodUpdate): Observable<Period> {
    return this.http.put<Period>(`${this.API_URL}${id}`, updates).pipe(
      tap(updatedPeriod => {
        this.periods.update(pers =>
          pers.map(per => per._id === id ? updatedPeriod : per)
        );

        // Actualizar período activo si corresponde
        if (updatedPeriod.tipo_periodo === TipoPeriodo.MENSUAL_ESTANDAR &&
            updatedPeriod.estado === EstadoPeriodo.ACTIVO) {
          this.activeMensualPeriod.set(updatedPeriod);
        } else if (updatedPeriod.tipo_periodo === TipoPeriodo.CICLO_CREDITO &&
                   updatedPeriod.estado === EstadoPeriodo.ACTIVO) {
          this.activeCreditPeriod.set(updatedPeriod);
        }
      })
    );
  }

  /**
   * Cerrar un período
   */
  closePeriod(id: string, fechaFin?: Date): Observable<Period> {
    const body = fechaFin ? { fecha_fin: fechaFin.toISOString() } : {};
    return this.http.post<Period>(`${this.API_URL}${id}/close`, body).pipe(
      tap(closedPeriod => {
        this.periods.update(pers =>
          pers.map(per => per._id === id ? closedPeriod : per)
        );

        // Limpiar período activo si corresponde
        if (closedPeriod.tipo_periodo === TipoPeriodo.MENSUAL_ESTANDAR) {
          this.activeMensualPeriod.set(null);
        } else {
          this.activeCreditPeriod.set(null);
        }
      })
    );
  }

  /**
   * Eliminar un período
   */
  deletePeriod(id: string): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}${id}`).pipe(
      tap(() => {
        this.periods.update(pers => pers.filter(per => per._id !== id));
      })
    );
  }

  /**
   * Inicializar períodos activos (mensual y crédito)
   */
  initializeActivePeriods(): void {
    this.getActivePeriod(TipoPeriodo.MENSUAL_ESTANDAR).subscribe();
    this.getActivePeriod(TipoPeriodo.CICLO_CREDITO).subscribe();
  }

  /**
   * Calcular liquidez según LOGICA_SISTEMA.md
   * liquidez = sueldo - meta_ahorro - total_arriendo_real - credito_periodo_anterior
   */
  calculateLiquidez(summary: PeriodSummary): number {
    return summary.liquidez_calculada;
  }

  /**
   * Calcular crédito disponible real
   * credito_usable_real = meta_credito - total_gastos_credito + total_aportes_credito
   */
  calculateCreditoDisponible(summary: PeriodSummary): number {
    const creditoCategory = summary.categories_summary.find(
      cat => cat.categoria_slug === 'credito'
    );

    if (!creditoCategory || !creditoCategory.meta) {
      return 0;
    }

    return creditoCategory.meta - creditoCategory.total_real;
  }
}
