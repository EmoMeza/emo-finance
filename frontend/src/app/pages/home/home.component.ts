import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { PeriodService, Period, TipoPeriodo } from '../../services/period.service';
import { CategoryService, TipoCategoria } from '../../services/category.service';
import { ExpenseService } from '../../services/expense.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  isLoading = signal(true);
  error = signal('');
  showConfigModal = signal(false);
  creditPeriod = signal<Period | null>(null);
  isFirstTimeSetup = signal(false);

  // Computed signals para las 4 categorías
  ahorroCategory = computed(() =>
    this.categoryService.getCategoryByType(TipoCategoria.AHORRO)
  );
  arriendoCategory = computed(() =>
    this.categoryService.getCategoryByType(TipoCategoria.ARRIENDO)
  );
  creditoCategory = computed(() =>
    this.categoryService.getCategoryByType(TipoCategoria.CREDITO)
  );
  liquidoCategory = computed(() =>
    this.categoryService.getCategoryByType(TipoCategoria.LIQUIDO)
  );

  // Computed para los valores de las categorías desde el período activo
  ahorro = computed(() => this.periodService.activePeriod()?.metas_categorias.ahorro ?? 0);
  arriendo = computed(() => this.periodService.activePeriod()?.metas_categorias.arriendo ?? 0);
  creditoUsable = computed(() => this.periodService.activePeriod()?.metas_categorias.credito_usable ?? 0);
  liquido = computed(() => this.periodService.activePeriod()?.liquido_calculado ?? 0);
  sueldo = computed(() => this.periodService.activePeriod()?.sueldo ?? 0);

  // Computed para porcentajes
  porcentajeAhorro = computed(() => this.calculatePercentage(this.ahorro()));
  porcentajeArriendo = computed(() => this.calculatePercentage(this.arriendo()));
  porcentajeCredito = computed(() => this.calculatePercentage(this.creditoUsable()));
  porcentajeLiquido = computed(() => this.calculatePercentage(this.liquido()));

  // Computed para detectar si el período está sin configurar
  isPeriodUnconfigured = computed(() => {
    const period = this.periodService.activePeriod();
    return period && period.sueldo === 0;
  });

  // Valores del formulario de configuración
  configForm = {
    sueldo: 0,
    ahorro: 0,
    arriendo: 0,
    credito: 0,
    deudaCreditoAnterior: 0  // Para usuarios nuevos: deuda del período de crédito anterior
  };

  // Computed para líquido calculado en tiempo real en el modal
  liquidoPreview = computed(() => {
    return this.configForm.sueldo - this.configForm.ahorro - this.configForm.arriendo - this.configForm.deudaCreditoAnterior;
  });

  constructor(
    public authService: AuthService,
    public periodService: PeriodService,
    public categoryService: CategoryService,
    private expenseService: ExpenseService
  ) {}

  ngOnInit() {
    this.loadDashboardData();
  }

  async loadDashboardData() {
    try {
      this.isLoading.set(true);
      this.error.set('');

      // Cargar categorías primero
      await this.loadCategories();

      // Cargar período activo (ahora siempre existirá gracias al auto-create en backend)
      await this.loadActivePeriod();

      // Cargar período de crédito
      await this.loadCreditPeriod();

      // Detectar si es la primera vez (período sin configurar Y período de crédito con total_gastado = 0)
      const period = this.periodService.activePeriod();
      const credit = this.creditPeriod();
      this.isFirstTimeSetup.set(period?.sueldo === 0 && credit?.total_gastado === 0);

      // Si el período está sin configurar (sueldo = 0), mostrar modal automáticamente
      if (this.isPeriodUnconfigured()) {
        this.openConfigModal();
      }

      this.isLoading.set(false);
    } catch (err: any) {
      console.error('Error loading dashboard:', err);
      this.error.set(err.error?.detail || 'Error al cargar el dashboard');
      this.isLoading.set(false);
    }
  }

  private loadCategories(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.categoryService.getCategories().subscribe({
        next: (categories) => {
          // Si no hay categorías, inicializar las predeterminadas
          if (categories.length === 0) {
            this.categoryService.initializeDefaultCategories().subscribe({
              next: () => resolve(),
              error: (err) => reject(err)
            });
          } else {
            resolve();
          }
        },
        error: (err) => reject(err)
      });
    });
  }

  private loadActivePeriod(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.periodService.getActivePeriod(TipoPeriodo.MENSUAL_ESTANDAR).subscribe({
        next: () => resolve(),
        error: (err) => reject(err)
      });
    });
  }

  private loadCreditPeriod(): Promise<void> {
    return new Promise((resolve) => {
      this.periodService.getActivePeriod(TipoPeriodo.CICLO_CREDITO).subscribe({
        next: (period) => {
          this.creditPeriod.set(period);
          resolve();
        },
        error: (err) => {
          // Si no hay período de crédito, no es crítico
          console.warn('No credit period found:', err);
          resolve();
        }
      });
    });
  }

  private calculatePercentage(value: number): number {
    const total = this.sueldo();
    return total > 0 ? Math.round((value / total) * 100) : 0;
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0
    }).format(value);
  }

  openConfigModal() {
    // Inicializar valores del formulario con los actuales del período
    const period = this.periodService.activePeriod();
    if (period) {
      this.configForm.sueldo = period.sueldo;
      this.configForm.ahorro = period.metas_categorias.ahorro;
      this.configForm.arriendo = period.metas_categorias.arriendo;
      this.configForm.credito = period.metas_categorias.credito_usable;
    }
    this.showConfigModal.set(true);
  }

  closeConfigModal() {
    this.showConfigModal.set(false);
  }

  async savePeriodConfig() {
    const period = this.periodService.activePeriod();
    if (!period) return;

    try {
      // Actualizar período mensual
      await this.periodService.updatePeriod(period._id, {
        sueldo: this.configForm.sueldo,
        metas_categorias: {
          ahorro: this.configForm.ahorro,
          arriendo: this.configForm.arriendo,
          credito_usable: this.configForm.credito
        }
      }).toPromise();

      // Si es primera vez, actualizar el período de crédito con la deuda anterior
      if (this.isFirstTimeSetup() && this.creditPeriod()) {
        await this.periodService.updatePeriod(this.creditPeriod()!._id, {
          total_gastado: this.configForm.deudaCreditoAnterior
        }).toPromise();
      }

      this.closeConfigModal();
      // Recargar para obtener los períodos actualizados
      await this.loadActivePeriod();
      await this.loadCreditPeriod();
    } catch (err: any) {
      console.error('Error saving period config:', err);
      this.error.set(err.error?.detail || 'Error al guardar la configuración');
    }
  }

  calculatePercentagePreview(value: number): number {
    return this.configForm.sueldo > 0 ? Math.round((value / this.configForm.sueldo) * 100) : 0;
  }
}
