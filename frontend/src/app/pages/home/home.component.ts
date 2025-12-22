import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { PeriodService } from '../../services/period.service';
import { CategoryService } from '../../services/category.service';
import { ExpenseService } from '../../services/expense.service';
import { Period, TipoPeriodo, Category } from '../../models';
import { InitialSetupModalComponent } from '../../components/initial-setup-modal/initial-setup-modal.component';
import { CategoryDetailModalComponent } from '../../components/category-detail-modal/category-detail-modal.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule, InitialSetupModalComponent, CategoryDetailModalComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  isLoading = signal(true);
  error = signal('');
  showInitialSetupModal = signal(false);
  showCategoryModal = signal(false);
  selectedCategory = signal<Category | null>(null);
  selectedCategoryMeta = signal<number | undefined>(undefined);
  selectedPeriodId = signal<string>('');
  creditPeriod = signal<Period | null>(null);
  isFirstTimeSetup = signal(false);

  // Computed signals para las 4 categorías
  ahorroCategory = computed(() =>
    this.categoryService.getAhorroCategory()
  );
  arriendoCategory = computed(() =>
    this.categoryService.getArriendoCategory()
  );
  creditoCategory = computed(() =>
    this.categoryService.getCreditoCategory()
  );
  liquidoCategory = computed(() =>
    this.categoryService.getLiquidezCategory()
  );

  // Computed para obtener resúmenes de categorías desde el period summary
  ahorroSummary = computed(() =>
    this.periodService.currentSummary()?.categories_summary.find(
      c => c.categoria_slug === 'ahorro'
    )
  );

  arriendoSummary = computed(() =>
    this.periodService.currentSummary()?.categories_summary.find(
      c => c.categoria_slug === 'arriendo'
    )
  );

  creditoSummary = computed(() =>
    this.periodService.currentSummary()?.categories_summary.find(
      c => c.categoria_slug === 'credito'
    )
  );

  liquidoSummary = computed(() =>
    this.periodService.currentSummary()?.categories_summary.find(
      c => c.categoria_slug === 'liquidez'
    )
  );

  // Computed para los valores de las categorías (total real)
  ahorro = computed(() => this.ahorroSummary()?.total_real ?? 0);
  arriendo = computed(() => this.arriendoSummary()?.total_real ?? 0);
  creditoUsable = computed(() => this.creditoSummary()?.total_real ?? 0);
  liquido = computed(() => this.periodService.currentSummary()?.liquidez_calculada ?? 0);
  sueldo = computed(() => this.periodService.activeMensualPeriod()?.sueldo ?? 0);

  // Computed para metas de categorías
  // NOTA: Solo Crédito tiene meta real. Ahorro y Arriendo usan total_real
  metaCredito = computed(() => this.creditoSummary()?.meta ?? 0);

  // Computed para porcentajes
  porcentajeAhorro = computed(() => this.calculatePercentage(this.ahorro()));
  porcentajeArriendo = computed(() => this.calculatePercentage(this.arriendo()));
  porcentajeCredito = computed(() => this.calculatePercentage(this.creditoUsable()));
  porcentajeLiquido = computed(() => this.calculatePercentage(this.liquido()));

  // Computed para detectar si el período está sin configurar
  isPeriodUnconfigured = computed(() => {
    const period = this.periodService.activeMensualPeriod();
    return period && period.sueldo === 0;
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
      const period = this.periodService.activeMensualPeriod();
      const credit = this.creditPeriod();
      this.isFirstTimeSetup.set(period?.sueldo === 0 && credit?.total_gastado === 0);

      // Si el período está sin configurar (sueldo = 0), mostrar modal automáticamente
      if (this.isPeriodUnconfigured()) {
        this.openInitialSetupModal();
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
            this.categoryService.initDefaultCategories().subscribe({
              next: () => resolve(),
              error: (err: any) => reject(err)
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
        next: (period) => {
          // Cargar resumen del período con totales reales de categorías
          if (period) {
            this.periodService.getPeriodSummary(period._id).subscribe({
              next: () => resolve(),
              error: (err) => {
                console.warn('Error loading period summary:', err);
                resolve(); // No es crítico si falla el summary
              }
            });
          } else {
            resolve();
          }
        },
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

  // ==================
  // INITIAL SETUP MODAL
  // ==================

  openInitialSetupModal() {
    this.showInitialSetupModal.set(true);
  }

  closeInitialSetupModal() {
    this.showInitialSetupModal.set(false);
  }

  async onInitialSetupComplete() {
    try {
      // Recargar datos del dashboard (esto también carga el summary)
      await this.loadActivePeriod();
      await this.loadCreditPeriod();

      // Cerrar modal solo después de recargar todos los datos
      this.closeInitialSetupModal();
    } catch (err: any) {
      console.error('Error reloading dashboard after setup:', err);
      this.error.set('Error al recargar el dashboard');
      this.closeInitialSetupModal();
    }
  }

  // ==================
  // CATEGORY DETAIL MODAL
  // ==================

  openCategoryModal(category: Category, periodId: string, meta?: number) {
    this.selectedCategory.set(category);
    this.selectedCategoryMeta.set(meta);
    this.selectedPeriodId.set(periodId);
    this.showCategoryModal.set(true);
  }

  closeCategoryModal() {
    this.showCategoryModal.set(false);
    this.selectedCategory.set(null);
    this.selectedCategoryMeta.set(undefined);
    this.selectedPeriodId.set('');
  }

  // Métodos auxiliares para abrir modales de categorías específicas
  openAhorroModal() {
    const category = this.ahorroCategory();
    const periodId = this.periodService.activeMensualPeriod()?._id;
    if (category && periodId) {
      // Ahorro NO tiene meta, se calcula como suma de gastos - aportes
      this.openCategoryModal(category, periodId, undefined);
    }
  }

  openArriendoModal() {
    const category = this.arriendoCategory();
    const periodId = this.periodService.activeMensualPeriod()?._id;
    if (category && periodId) {
      // Arriendo NO tiene meta, se calcula como suma de gastos - aportes
      this.openCategoryModal(category, periodId, undefined);
    }
  }

  openCreditoModal() {
    const category = this.creditoCategory();
    const periodId = this.creditPeriod()?._id; // Usa período de crédito
    if (category && periodId) {
      this.openCategoryModal(category, periodId, this.metaCredito());
    }
  }

  openLiquidoModal() {
    const category = this.liquidoCategory();
    const periodId = this.periodService.activeMensualPeriod()?._id;
    if (category && periodId) {
      // Liquidez no tiene meta fija, se calcula automáticamente
      this.openCategoryModal(category, periodId, undefined);
    }
  }
}
