import { Component, OnInit, OnDestroy, ChangeDetectionStrategy } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { OrderService } from '../services/order.service';

interface Order {
  id: number;
  reference: string;
  status: string;
  totalAmount: number;
  createdDate: string;
}

const PAGE_SIZE = 20;
const ACTIVE_STATUSES = ['Active', 'Pending'];

@Component({
  selector: 'app-order-list',
  templateUrl: './order-list.component.html',
  styleUrls: ['./order-list.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class OrderListComponent implements OnInit, OnDestroy {

  orders: Order[] = [];
  isLoading = false;
  errorMessage = '';
  currentPage = 1;

  private destroy$ = new Subject<void>();

  constructor(private orderService: OrderService) {}

  ngOnInit(): void {
    this.loadOrders();
  }

  loadOrders(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.orderService.getOrders(this.currentPage, PAGE_SIZE)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (orders: Order[]) => {
          this.orders = orders;
          this.isLoading = false;
        },
        error: () => {
          this.errorMessage = 'Unable to load orders. Please try again.';
          this.isLoading = false;
        }
      });
  }

  getActiveOrders(): Order[] {
    return this.orderService.filterByStatus(this.orders, ACTIVE_STATUSES);
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadOrders();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
