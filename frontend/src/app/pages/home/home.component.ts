import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { PeriodService } from '../../services/period.service';
import { CategoryService } from '../../services/category.service';
import { ExpenseService } from '../../services/expense.service';
import { AporteService } from '../../services/aporte.service';
import { Period, TipoPeriodo, Category, TipoGasto } from '../../models';
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
  showEditSueldoModal = signal(false);
  editSueldoValue = signal(0);
  showQuickAddModal = signal(false);

  // Form para agregar gasto/aporte rápido
  quickAddForm = {
    tipoRegistro: signal<'gasto' | 'aporte'>('gasto'),
    tipoGasto: signal<'fijo' | 'variable'>('variable'),
    categoriaId: '',
    nombre: '',
    monto: 0,
    descripcion: '',
    esPermanente: false,
    periodosRestantes: 1,
    esAporteFijo: false
  };

  selectedCategory = signal<Category | null>(null);
  selectedCategoryMeta = signal<number | undefined>(undefined);
  selectedPeriodId = signal<string>('');
  selectedPeriodFechaInicio = signal<Date | undefined>(undefined);
  selectedPeriodFechaFin = signal<Date | undefined>(undefined);
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
  ahorro = computed(() => {
    const summary = this.ahorroSummary();
    console.log('DEBUG: ahorroSummary', summary);
    return summary?.total_real ?? 0;
  });
  arriendo = computed(() => {
    const summary = this.arriendoSummary();
    console.log('DEBUG: arriendoSummary', summary);
    return summary?.total_real ?? 0;
  });
  creditoUsable = computed(() => {
    const summary = this.creditoSummary();
    console.log('DEBUG: creditoSummary', summary);
    return summary?.total_real ?? 0;
  });
  liquido = computed(() => {
    const liquidez = this.periodService.currentSummary()?.liquidez_calculada ?? 0;
    console.log('DEBUG: liquidez_calculada', liquidez);
    return liquidez;
  });
  sueldo = computed(() => this.periodService.activeMensualPeriod()?.sueldo ?? 0);

  // Computed para metas de categorías
  // NOTA: Solo Crédito tiene meta real. Ahorro y Arriendo usan total_real
  metaCredito = computed(() => {
    // La meta de crédito viene del período de crédito, no del mensual
    const creditPeriod = this.creditPeriod();
    const meta = creditPeriod?.metas_categorias?.credito_usable ?? 0;
    console.log('DEBUG: metaCredito computed', { creditPeriod, meta });
    return meta;
  });

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
    private expenseService: ExpenseService,
    private aporteService: AporteService
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
      // Cerrar modal primero
      this.closeInitialSetupModal();

      // Recargar TODO el dashboard para refrescar los datos
      await this.loadDashboardData();
    } catch (err: any) {
      console.error('Error reloading dashboard after setup:', err);
      this.error.set('Error al recargar el dashboard');
    }
  }

  // ==================
  // CATEGORY DETAIL MODAL
  // ==================

  openCategoryModal(
    category: Category,
    periodId: string,
    meta?: number,
    fechaInicio?: Date,
    fechaFin?: Date
  ) {
    this.selectedCategory.set(category);
    this.selectedCategoryMeta.set(meta);
    this.selectedPeriodId.set(periodId);
    this.selectedPeriodFechaInicio.set(fechaInicio);
    this.selectedPeriodFechaFin.set(fechaFin);
    this.showCategoryModal.set(true);
  }

  async closeCategoryModal() {
    this.showCategoryModal.set(false);
    this.selectedCategory.set(null);
    this.selectedCategoryMeta.set(undefined);
    this.selectedPeriodId.set('');
    this.selectedPeriodFechaInicio.set(undefined);
    this.selectedPeriodFechaFin.set(undefined);

    // Recargar el summary para actualizar los totales en el dashboard
    const period = this.periodService.activeMensualPeriod();
    if (period) {
      this.periodService.getPeriodSummary(period._id).subscribe({
        error: (err) => console.error('Error reloading summary:', err)
      });
    }
  }

  async onMetaChanged(newMeta: number) {
    // Actualizar la meta en el período correspondiente
    const category = this.selectedCategory();
    const periodId = this.selectedPeriodId();

    if (!category || !periodId) return;

    try {
      // TODO: Implementar endpoint para actualizar meta del período
      console.log('META CHANGED:', {
        category: category.slug,
        periodId,
        newMeta
      });

      // Por ahora, solo actualizar localmente y recargar
      this.selectedCategoryMeta.set(newMeta);

      // Recargar summary
      this.periodService.getPeriodSummary(periodId).subscribe({
        next: () => {
          console.log('Summary recargado después de cambiar meta');
        },
        error: (err) => console.error('Error reloading summary:', err)
      });
    } catch (error) {
      console.error('Error updating meta:', error);
      alert('Error al actualizar la meta');
    }
  }

  async onPeriodChanged() {
    // Recargar el período de crédito para obtener la fecha_fin actualizada
    try {
      await this.loadCreditPeriod();

      // Actualizar las fechas en el modal si está abierto
      const creditPeriod = this.creditPeriod();
      if (creditPeriod) {
        this.selectedPeriodFechaInicio.set(new Date(creditPeriod.fecha_inicio));
        this.selectedPeriodFechaFin.set(new Date(creditPeriod.fecha_fin));
      }
    } catch (error) {
      console.error('Error reloading period:', error);
    }
  }

  // Métodos auxiliares para abrir modales de categorías específicas
  openAhorroModal() {
    const category = this.ahorroCategory();
    const period = this.periodService.activeMensualPeriod();
    if (category && period) {
      // Ahorro NO tiene meta, se calcula como suma de gastos - aportes
      this.openCategoryModal(
        category,
        period._id,
        undefined,
        new Date(period.fecha_inicio),
        new Date(period.fecha_fin)
      );
    }
  }

  openArriendoModal() {
    const category = this.arriendoCategory();
    const period = this.periodService.activeMensualPeriod();
    if (category && period) {
      // Arriendo NO tiene meta, se calcula como suma de gastos - aportes
      this.openCategoryModal(
        category,
        period._id,
        undefined,
        new Date(period.fecha_inicio),
        new Date(period.fecha_fin)
      );
    }
  }

  openCreditoModal() {
    const category = this.creditoCategory();
    const period = this.creditPeriod(); // Usa período de crédito
    if (category && period) {
      this.openCategoryModal(
        category,
        period._id,
        this.metaCredito(),
        new Date(period.fecha_inicio),
        new Date(period.fecha_fin)
      );
    }
  }

  openLiquidoModal() {
    const category = this.liquidoCategory();
    const period = this.periodService.activeMensualPeriod();
    if (category && period) {
      // Liquidez no tiene meta fija, se calcula automáticamente
      this.openCategoryModal(
        category,
        period._id,
        undefined,
        new Date(period.fecha_inicio),
        new Date(period.fecha_fin)
      );
    }
  }

  // ==================
  // EDIT SUELDO MODAL
  // ==================

  openEditSueldoModal() {
    const currentSueldo = this.sueldo();
    this.editSueldoValue.set(currentSueldo);
    this.showEditSueldoModal.set(true);
  }

  closeEditSueldoModal() {
    this.showEditSueldoModal.set(false);
    this.editSueldoValue.set(0);
  }

  async saveEditSueldo() {
    const newSueldo = this.editSueldoValue();

    if (newSueldo <= 0) {
      alert('El sueldo debe ser mayor a 0');
      return;
    }

    const period = this.periodService.activeMensualPeriod();
    if (!period) {
      alert('No hay período activo');
      return;
    }

    try {
      await this.periodService.updatePeriod(period._id, { sueldo: newSueldo }).toPromise();
      this.closeEditSueldoModal();
      await this.loadDashboardData();
    } catch (error) {
      console.error('Error updating sueldo:', error);
      alert('Error al actualizar el sueldo');
    }
  }

  // ==================
  // QUICK ADD MODAL
  // ==================

  openQuickAddModal() {
    this.resetQuickAddForm();
    this.showQuickAddModal.set(true);
  }

  closeQuickAddModal() {
    this.showQuickAddModal.set(false);
    this.resetQuickAddForm();
  }

  resetQuickAddForm() {
    this.quickAddForm.tipoRegistro.set('gasto');
    this.quickAddForm.tipoGasto.set('variable');
    this.quickAddForm.categoriaId = '';
    this.quickAddForm.nombre = '';
    this.quickAddForm.monto = 0;
    this.quickAddForm.descripcion = '';
    this.quickAddForm.esPermanente = false;
    this.quickAddForm.periodosRestantes = 1;
    this.quickAddForm.esAporteFijo = false;
  }

  async saveQuickAdd() {
    const form = this.quickAddForm;

    // Validaciones
    if (!form.categoriaId) {
      alert('Debes seleccionar una categoría');
      return;
    }

    if (!form.nombre || form.nombre.trim() === '') {
      alert('Debes ingresar un nombre');
      return;
    }

    if (form.monto <= 0) {
      alert('El monto debe ser mayor a 0');
      return;
    }

    try {
      if (form.tipoRegistro() === 'gasto') {
        await this.saveQuickAddExpense();
      } else {
        await this.saveQuickAddAporte();
      }

      this.closeQuickAddModal();
      await this.loadDashboardData();
    } catch (error) {
      console.error('Error saving quick add:', error);
      alert('Error al guardar el registro');
    }
  }

  private async saveQuickAddExpense() {
    const form = this.quickAddForm;

    // Determinar el período correcto según la categoría
    let periodoId = '';

    if (form.categoriaId === this.creditoCategory()?._id) {
      // Gastos de crédito van al período de crédito
      const creditPeriod = this.creditPeriod();
      if (!creditPeriod) {
        throw new Error('No hay período de crédito activo');
      }
      periodoId = creditPeriod._id;
    } else {
      // Gastos de otras categorías van al período mensual
      const mensualPeriod = this.periodService.activeMensualPeriod();
      if (!mensualPeriod) {
        throw new Error('No hay período mensual activo');
      }
      periodoId = mensualPeriod._id;
    }

    const expenseData = {
      categoria_id: form.categoriaId,
      nombre: form.nombre,
      monto: form.monto,
      tipo: (form.tipoGasto() === 'fijo' ? TipoGasto.FIJO : TipoGasto.VARIABLE),
      es_permanente: form.tipoGasto() === 'fijo' ? form.esPermanente : undefined,
      periodos_restantes: form.tipoGasto() === 'fijo' && !form.esPermanente ? form.periodosRestantes : undefined,
      descripcion: form.descripcion || undefined
    };

    return new Promise<void>((resolve, reject) => {
      this.expenseService.createExpense(periodoId, expenseData).subscribe({
        next: () => resolve(),
        error: (err) => reject(err)
      });
    });
  }

  private async saveQuickAddAporte() {
    const form = this.quickAddForm;

    // Los aportes siempre van al período mensual
    const mensualPeriod = this.periodService.activeMensualPeriod();
    if (!mensualPeriod) {
      throw new Error('No hay período mensual activo');
    }

    const aporteData = {
      categoria_id: form.categoriaId,
      nombre: form.nombre,
      monto: form.monto,
      es_fijo: form.esAporteFijo,
      descripcion: form.descripcion || undefined
    };

    return new Promise<void>((resolve, reject) => {
      this.aporteService.createAporte(mensualPeriod._id, aporteData).subscribe({
        next: () => resolve(),
        error: (err) => reject(err)
      });
    });
  }
}
