import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { Category, CategoryCreate, CategoryUpdate, TipoCategoria } from '../models';

@Injectable({
  providedIn: 'root'
})
export class CategoryService {
  private readonly API_URL = `${environment.apiUrl}/categories/`;

  // Signal for reactive categories state
  categories = signal<Category[]>([]);
  isLoading = signal<boolean>(false);

  constructor(private http: HttpClient) {}

  /**
   * Obtener todas las categorías del usuario
   * Inicializa las 4 categorías por defecto si no existen
   */
  getCategories(): Observable<Category[]> {
    this.isLoading.set(true);
    return this.http.get<Category[]>(this.API_URL).pipe(
      tap(categories => {
        this.categories.set(categories);
        this.isLoading.set(false);
      })
    );
  }

  /**
   * Obtener una categoría por ID
   */
  getCategoryById(id: string): Observable<Category> {
    return this.http.get<Category>(`${this.API_URL}${id}`);
  }

  /**
   * Obtener una categoría por slug (ahorro, arriendo, credito, liquidez)
   */
  getCategoryBySlug(slug: TipoCategoria): Observable<Category> {
    return this.http.get<Category>(`${this.API_URL}by-slug/${slug}`);
  }

  /**
   * Crear una nueva categoría (generalmente no se usa)
   */
  createCategory(category: CategoryCreate): Observable<Category> {
    return this.http.post<Category>(this.API_URL, category).pipe(
      tap(newCategory => {
        this.categories.update(cats => [...cats, newCategory]);
      })
    );
  }

  /**
   * Inicializar las 4 categorías por defecto
   */
  initDefaultCategories(): Observable<Category[]> {
    this.isLoading.set(true);
    return this.http.post<Category[]>(`${this.API_URL}init-defaults`, {}).pipe(
      tap(categories => {
        this.categories.set(categories);
        this.isLoading.set(false);
      })
    );
  }

  /**
   * Actualizar una categoría
   */
  updateCategory(id: string, updates: CategoryUpdate): Observable<Category> {
    return this.http.put<Category>(`${this.API_URL}${id}`, updates).pipe(
      tap(updatedCategory => {
        this.categories.update(cats =>
          cats.map(cat => cat._id === id ? updatedCategory : cat)
        );
      })
    );
  }

  /**
   * Eliminar una categoría
   */
  deleteCategory(id: string): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}${id}`).pipe(
      tap(() => {
        this.categories.update(cats => cats.filter(cat => cat._id !== id));
      })
    );
  }

  /**
   * Obtener categoría de Ahorro
   */
  getAhorroCategory(): Category | undefined {
    return this.categories().find(cat => cat.slug === TipoCategoria.AHORRO);
  }

  /**
   * Obtener categoría de Arriendo
   */
  getArriendoCategory(): Category | undefined {
    return this.categories().find(cat => cat.slug === TipoCategoria.ARRIENDO);
  }

  /**
   * Obtener categoría de Crédito
   */
  getCreditoCategory(): Category | undefined {
    return this.categories().find(cat => cat.slug === TipoCategoria.CREDITO);
  }

  /**
   * Obtener categoría de Liquidez
   */
  getLiquidezCategory(): Category | undefined {
    return this.categories().find(cat => cat.slug === TipoCategoria.LIQUIDEZ);
  }
}
