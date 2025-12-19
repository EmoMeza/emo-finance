import { Injectable, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

export enum TipoPeriodo {
  MENSUAL_ESTANDAR = 'mensual_estandar',
  CICLO_CREDITO = 'ciclo_credito'
}

export enum EstadoPeriodo {
  ACTIVO = 'activo',
  CERRADO = 'cerrado',
  PROYECTADO = 'proyectado'
}

export interface MetasCategorias {
  ahorro: number;
  arriendo: number;
  credito_usable: number;
}

export interface Period {
  _id: string;
  user_id: string;
  tipo_periodo: TipoPeriodo;
  fecha_inicio: string;
  fecha_fin: string;
  sueldo: number;
  metas_categorias: MetasCategorias;
  estado: EstadoPeriodo;
  total_gastado: number;
  liquido_calculado: number;
  created_at: string;
  updated_at: string;
}

export interface PeriodCreate {
  tipo_periodo: TipoPeriodo;
  fecha_inicio: string;
  fecha_fin: string;
  sueldo: number;
  metas_categorias: MetasCategorias;
  estado?: EstadoPeriodo;
}

export interface PeriodUpdate {
  sueldo?: number;
  metas_categorias?: MetasCategorias;
  estado?: EstadoPeriodo;
  total_gastado?: number;
}

@Injectable({
  providedIn: 'root'
})
export class PeriodService {
  private readonly API_URL = environment.apiUrl;

  // Signal para el período activo
  activePeriod = signal<Period | null>(null);
  periods = signal<Period[]>([]);

  constructor(private http: HttpClient) {}

  createPeriod(periodData: PeriodCreate): Observable<Period> {
    return this.http.post<Period>(`${this.API_URL}/periods/`, periodData).pipe(
      tap(period => {
        if (period.estado === EstadoPeriodo.ACTIVO) {
          this.activePeriod.set(period);
        }
      })
    );
  }

  getPeriods(
    skip: number = 0,
    limit: number = 10,
    estado?: EstadoPeriodo,
    tipoPeriodo?: TipoPeriodo
  ): Observable<Period[]> {
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (estado) {
      params = params.set('estado', estado);
    }
    if (tipoPeriodo) {
      params = params.set('tipo_periodo', tipoPeriodo);
    }

    return this.http.get<Period[]>(`${this.API_URL}/periods/`, { params }).pipe(
      tap(periods => this.periods.set(periods))
    );
  }

  getActivePeriod(tipoPeriodo?: TipoPeriodo): Observable<Period> {
    let params = new HttpParams();
    if (tipoPeriodo) {
      params = params.set('tipo_periodo', tipoPeriodo);
    }

    return this.http.get<Period>(`${this.API_URL}/periods/active`, { params }).pipe(
      tap(period => this.activePeriod.set(period))
    );
  }

  getPeriodById(periodId: string): Observable<Period> {
    return this.http.get<Period>(`${this.API_URL}/periods/${periodId}`);
  }

  updatePeriod(periodId: string, updateData: PeriodUpdate): Observable<Period> {
    return this.http.put<Period>(`${this.API_URL}/periods/${periodId}`, updateData).pipe(
      tap(period => {
        if (period.estado === EstadoPeriodo.ACTIVO) {
          this.activePeriod.set(period);
        }
      })
    );
  }

  closePeriod(periodId: string): Observable<Period> {
    return this.http.post<Period>(`${this.API_URL}/periods/${periodId}/close`, {}).pipe(
      tap(() => {
        // Si cerramos el período activo, limpiar signal
        if (this.activePeriod()?._id === periodId) {
          this.activePeriod.set(null);
        }
      })
    );
  }

  deletePeriod(periodId: string): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/periods/${periodId}`).pipe(
      tap(() => {
        if (this.activePeriod()?._id === periodId) {
          this.activePeriod.set(null);
        }
      })
    );
  }

  calculateLiquido(sueldo: number, metas: MetasCategorias): number {
    return sueldo - metas.ahorro - metas.arriendo - metas.credito_usable;
  }
}
