import { Injectable, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

export enum TipoCategoria {
  AHORRO = 'ahorro',
  ARRIENDO = 'arriendo',
  CREDITO = 'credito',
  LIQUIDO = 'liquido'
}

export interface Subcategoria {
  nombre: string;
  color?: string;
  descripcion?: string;
}

export interface Category {
  _id: string;
  user_id: string;
  nombre: string;
  tipo: TipoCategoria;
  color: string;
  icono?: string;
  subcategorias: Subcategoria[];
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate {
  nombre: string;
  tipo: TipoCategoria;
  color?: string;
  icono?: string;
  subcategorias?: Subcategoria[];
}

export interface CategoryUpdate {
  nombre?: string;
  color?: string;
  icono?: string;
  subcategorias?: Subcategoria[];
}

@Injectable({
  providedIn: 'root'
})
export class CategoryService {
  private readonly API_URL = environment.apiUrl;

  // Signals para categorías
  categories = signal<Category[]>([]);
  categoriesByType = signal<Map<TipoCategoria, Category>>(new Map());

  constructor(private http: HttpClient) {}

  createCategory(categoryData: CategoryCreate): Observable<Category> {
    return this.http.post<Category>(`${this.API_URL}/categories/`, categoryData);
  }

  getCategories(tipo?: TipoCategoria): Observable<Category[]> {
    let params = new HttpParams();
    if (tipo) {
      params = params.set('tipo', tipo);
    }

    return this.http.get<Category[]>(`${this.API_URL}/categories/`, { params }).pipe(
      tap(categories => {
        this.categories.set(categories);

        // Organizar por tipo
        const byType = new Map<TipoCategoria, Category>();
        categories.forEach(cat => byType.set(cat.tipo, cat));
        this.categoriesByType.set(byType);
      })
    );
  }

  initializeDefaultCategories(): Observable<Category[]> {
    return this.http.post<Category[]>(`${this.API_URL}/categories/init-defaults`, {}).pipe(
      tap(categories => {
        this.categories.set(categories);

        const byType = new Map<TipoCategoria, Category>();
        categories.forEach(cat => byType.set(cat.tipo, cat));
        this.categoriesByType.set(byType);
      })
    );
  }

  getCategoryById(categoryId: string): Observable<Category> {
    return this.http.get<Category>(`${this.API_URL}/categories/${categoryId}`);
  }

  updateCategory(categoryId: string, updateData: CategoryUpdate): Observable<Category> {
    return this.http.put<Category>(`${this.API_URL}/categories/${categoryId}`, updateData);
  }

  deleteCategory(categoryId: string): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/categories/${categoryId}`);
  }

  getCategoryByType(tipo: TipoCategoria): Category | undefined {
    return this.categoriesByType().get(tipo);
  }
}
