import { Injectable, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { Aporte, AporteCreate, AporteUpdate } from '../models';

@Injectable({
  providedIn: 'root'
})
export class AporteService {
  private readonly API_URL = `${environment.apiUrl}/aportes`;

  // Signal for reactive aportes state
  aportes = signal<Aporte[]>([]);
  isLoading = signal<boolean>(false);

  constructor(private http: HttpClient) {}

  /**
   * Obtener todos los aportes de un período
   */
  getAportes(
    periodoId: string,
    esFijo?: boolean,
    categoriaId?: string
  ): Observable<Aporte[]> {
    this.isLoading.set(true);

    let params = new HttpParams().set('periodo_id', periodoId);

    if (esFijo !== undefined) {
      params = params.set('es_fijo', esFijo.toString());
    }

    if (categoriaId) {
      params = params.set('categoria_id', categoriaId);
    }

    return this.http.get<Aporte[]>(this.API_URL, { params }).pipe(
      tap(aportes => {
        this.aportes.set(aportes);
        this.isLoading.set(false);
      })
    );
  }

  /**
   * Obtener un aporte por ID
   */
  getAporteById(id: string): Observable<Aporte> {
    return this.http.get<Aporte>(`${this.API_URL}/${id}`);
  }

  /**
   * Crear un nuevo aporte
   */
  createAporte(periodoId: string, aporte: AporteCreate): Observable<Aporte> {
    const params = new HttpParams().set('periodo_id', periodoId);

    return this.http.post<Aporte>(this.API_URL, aporte, { params }).pipe(
      tap(newAporte => {
        this.aportes.update(aps => [...aps, newAporte]);
      })
    );
  }

  /**
   * Actualizar un aporte
   */
  updateAporte(id: string, updates: AporteUpdate): Observable<Aporte> {
    return this.http.put<Aporte>(`${this.API_URL}/${id}`, updates).pipe(
      tap(updatedAporte => {
        this.aportes.update(aps =>
          aps.map(ap => ap._id === id ? updatedAporte : ap)
        );
      })
    );
  }

  /**
   * Eliminar un aporte
   */
  deleteAporte(id: string): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/${id}`).pipe(
      tap(() => {
        this.aportes.update(aps => aps.filter(ap => ap._id !== id));
      })
    );
  }

  /**
   * Obtener aportes fijos de un período
   */
  getAportesFijos(periodoId: string, categoriaId?: string): Observable<Aporte[]> {
    return this.getAportes(periodoId, true, categoriaId);
  }

  /**
   * Obtener aportes variables de un período
   */
  getAportesVariables(periodoId: string, categoriaId?: string): Observable<Aporte[]> {
    return this.getAportes(periodoId, false, categoriaId);
  }

  /**
   * Calcular total de aportes de una categoría
   */
  getTotalByCategoria(categoriaId: string): number {
    return this.aportes()
      .filter(ap => ap.categoria_id === categoriaId)
      .reduce((sum, ap) => sum + ap.monto, 0);
  }

  /**
   * Calcular total de todos los aportes
   */
  getTotal(): number {
    return this.aportes().reduce((sum, ap) => sum + ap.monto, 0);
  }
}
