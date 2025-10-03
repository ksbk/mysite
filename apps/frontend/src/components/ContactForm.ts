// apps/frontend/src/components/ContactForm.ts
/**
 * ContactForm TypeScript Component
 *
 * Purpose: Enhance HTML contact form with AJAX submission and real-time validation
 *
 * What it does:
 * - Intercepts form submission to prevent page reload
 * - Sends AJAX requests to Django API endpoint
 * - Handles success/error responses with smooth UI updates
 * - Provides real-time validation and loading states
 *
 * Why TypeScript:
 * - Type safety for API responses and form data
 * - Better development experience with autocomplete
 * - Catches errors at compile time
 * - Self-documenting code with interfaces
 */

// Type definitions for our API responses
interface ContactFormData {
  name: string;
  email: string;
  subject: string;
  message: string;
}

interface APISuccessResponse {
  success: true;
  message: string;
  data: {
    id: number;
    created_at: string;
  };
}

interface APIErrorResponse {
  success: false;
  message: string;
  errors: Record<string, string[]>;
}

type APIResponse = APISuccessResponse | APIErrorResponse;

/**
 * ContactForm class handles AJAX form submission
 */
export class ContactForm {
  private form: HTMLFormElement;
  private submitButton: HTMLButtonElement;
  private apiUrl: string;
  private csrfToken: string;

  constructor(formElement: HTMLFormElement) {
    this.form = formElement;
    this.submitButton = formElement.querySelector(
      'button[type="submit"]',
    ) as HTMLButtonElement;
    this.apiUrl = "/contact/api/";

    // Get CSRF token from Django
    this.csrfToken = this.getCSRFToken();

    // Set up event listeners
    this.init();
  }

  /**
   * Initialize the component - set up event listeners
   */
  private init(): void {
    // Prevent default form submission and handle with AJAX
    this.form.addEventListener("submit", (e) => {
      e.preventDefault();
      this.handleSubmit();
    });

    // Add real-time validation
    this.setupRealTimeValidation();

    console.log("🚀 ContactForm initialized with AJAX submission");
  }

  /**
   * Get CSRF token from Django
   */
  private getCSRFToken(): string {
    // Try to get from meta tag first
    const metaToken = document.querySelector(
      'meta[name="csrf-token"]',
    ) as HTMLMetaElement;
    if (metaToken) {
      return metaToken.content;
    }

    // Fallback: get from form's csrf_token input
    const csrfInput = this.form.querySelector(
      'input[name="csrfmiddlewaretoken"]',
    ) as HTMLInputElement;
    return csrfInput ? csrfInput.value : "";
  }

  /**
   * Handle form submission with AJAX
   */
  private async handleSubmit(): Promise<void> {
    try {
      // Show loading state
      this.setLoadingState(true);
      this.clearErrors();

      // Get form data
      const formData = this.getFormData();

      // Validate on frontend first (optional - Django will validate too)
      const clientValidation = this.validateForm(formData);
      if (!clientValidation.isValid) {
        this.displayErrors(clientValidation.errors);
        this.setLoadingState(false);
        return;
      }

      // Send AJAX request to Django API
      const response = await this.submitToAPI(formData);

      if (response.success) {
        this.handleSuccess(response);
      } else {
        this.handleError(response);
      }
    } catch (error) {
      console.error("Form submission error:", error);
      this.handleNetworkError();
    } finally {
      this.setLoadingState(false);
    }
  }

  /**
   * Extract form data into typed object
   */
  private getFormData(): ContactFormData {
    const formData = new FormData(this.form);

    return {
      name: (formData.get("name") as string)?.trim() || "",
      email: (formData.get("email") as string)?.trim() || "",
      subject: (formData.get("subject") as string)?.trim() || "",
      message: (formData.get("message") as string)?.trim() || "",
    };
  }

  /**
   * Client-side validation (runs before sending to server)
   */
  private validateForm(data: ContactFormData): {
    isValid: boolean;
    errors: Record<string, string[]>;
  } {
    const errors: Record<string, string[]> = {};

    // Required fields
    if (!data.name) {
      errors.name = ["Name is required."];
    }

    if (!data.email) {
      errors.email = ["Email is required."];
    } else if (!this.isValidEmail(data.email)) {
      errors.email = ["Please enter a valid email address."];
    }

    if (!data.message) {
      errors.message = ["Message is required."];
    } else if (data.message.length < 10) {
      errors.message = [
        "Please provide a more detailed message (at least 10 characters).",
      ];
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors,
    };
  }

  /**
   * Simple email validation
   */
  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Send form data to Django API
   */
  private async submitToAPI(data: ContactFormData): Promise<APIResponse> {
    const response = await fetch(this.apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": this.csrfToken,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Handle successful form submission
   */
  private handleSuccess(response: APISuccessResponse): void {
    console.log("✅ Form submitted successfully:", response);

    // Show success message
    this.showSuccessMessage(response.message);

    // Reset form
    this.form.reset();

    // Optional: Track analytics
    this.trackEvent("contact_form_submitted", { id: response.data.id });
  }

  /**
   * Handle form validation errors
   */
  private handleError(response: APIErrorResponse): void {
    console.log("❌ Form validation errors:", response.errors);

    this.displayErrors(response.errors);
    this.showErrorMessage(response.message);
  }

  /**
   * Handle network/server errors
   */
  private handleNetworkError(): void {
    this.showErrorMessage(
      "Something went wrong. Please try again or contact us directly.",
    );
  }

  /**
   * Show/hide loading state on submit button
   */
  private setLoadingState(loading: boolean): void {
    if (loading) {
      this.submitButton.disabled = true;
      this.submitButton.innerHTML = `
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Sending...
            `;
    } else {
      this.submitButton.disabled = false;
      this.submitButton.innerHTML = "Send Message";
    }
  }

  /**
   * Display field-specific errors
   */
  private displayErrors(errors: Record<string, string[]>): void {
    Object.entries(errors).forEach(([fieldName, fieldErrors]) => {
      const field = this.form.querySelector(
        `[name="${fieldName}"]`,
      ) as HTMLInputElement;
      if (field) {
        // Add error styling
        field.classList.add("border-red-500", "focus:ring-red-500");
        field.classList.remove("border-slate-300", "focus:ring-blue-500");

        // Show error message
        const errorDiv = this.createErrorElement(fieldErrors[0]);
        const existingError =
          field.parentElement?.querySelector(".error-message");
        if (existingError) {
          existingError.remove();
        }
        field.parentElement?.appendChild(errorDiv);
      }
    });
  }

  /**
   * Clear all error states
   */
  private clearErrors(): void {
    // Remove error styling from all fields
    const fields = this.form.querySelectorAll("input, textarea");
    fields.forEach((field) => {
      field.classList.remove("border-red-500", "focus:ring-red-500");
      field.classList.add("border-slate-300", "focus:ring-blue-500");
    });

    // Remove error messages
    this.form.querySelectorAll(".error-message").forEach((el) => el.remove());
    this.form.querySelectorAll(".alert").forEach((el) => el.remove());
  }

  /**
   * Create error message element
   */
  private createErrorElement(message: string): HTMLElement {
    const div = document.createElement("div");
    div.className = "error-message mt-1 text-sm text-red-600";
    div.textContent = message;
    return div;
  }

  /**
   * Show success message
   */
  private showSuccessMessage(message: string): void {
    const alertDiv = document.createElement("div");
    alertDiv.className =
      "alert alert-success p-4 rounded-lg mb-4 bg-green-50 border border-green-200 text-green-800";
    alertDiv.textContent = message;

    this.form.parentElement?.insertBefore(alertDiv, this.form);

    // Auto-remove after 5 seconds
    setTimeout(() => alertDiv.remove(), 5000);
  }

  /**
   * Show error message
   */
  private showErrorMessage(message: string): void {
    const alertDiv = document.createElement("div");
    alertDiv.className =
      "alert alert-error p-4 rounded-lg mb-4 bg-red-50 border border-red-200 text-red-800";
    alertDiv.textContent = message;

    this.form.parentElement?.insertBefore(alertDiv, this.form);

    // Auto-remove after 5 seconds
    setTimeout(() => alertDiv.remove(), 5000);
  }

  /**
   * Set up real-time validation as user types
   */
  private setupRealTimeValidation(): void {
    const fields = this.form.querySelectorAll("input, textarea");

    fields.forEach((field) => {
      field.addEventListener("blur", () => {
        // Validate individual field when user leaves it
        const fieldName = (field as HTMLInputElement).name;
        const fieldValue = (field as HTMLInputElement).value.trim();

        this.validateSingleField(fieldName, fieldValue);
      });
    });
  }

  /**
   * Validate single field in real-time
   */
  private validateSingleField(fieldName: string, value: string): void {
    const errors: string[] = [];

    switch (fieldName) {
      case "name":
        if (!value) errors.push("Name is required.");
        break;
      case "email":
        if (!value) {
          errors.push("Email is required.");
        } else if (!this.isValidEmail(value)) {
          errors.push("Please enter a valid email address.");
        }
        break;
      case "message":
        if (!value) {
          errors.push("Message is required.");
        } else if (value.length < 10) {
          errors.push(
            "Please provide a more detailed message (at least 10 characters).",
          );
        }
        break;
    }

    const field = this.form.querySelector(
      `[name="${fieldName}"]`,
    ) as HTMLInputElement;
    if (field) {
      // Clear existing errors for this field
      const existingError =
        field.parentElement?.querySelector(".error-message");
      if (existingError) existingError.remove();

      if (errors.length > 0) {
        // Show error
        field.classList.add("border-red-500", "focus:ring-red-500");
        field.classList.remove("border-slate-300", "focus:ring-blue-500");

        const errorDiv = this.createErrorElement(errors[0]);
        field.parentElement?.appendChild(errorDiv);
      } else {
        // Clear error state
        field.classList.remove("border-red-500", "focus:ring-red-500");
        field.classList.add("border-slate-300", "focus:ring-blue-500");
      }
    }
  }

  /**
   * Track events for analytics (optional)
   */
  private trackEvent(eventName: string, data: any): void {
    // Integration point for analytics (Google Analytics, etc.)
    console.log(`📊 Event: ${eventName}`, data);
  }
}

/**
 * Mount function for our component system
 */
export function mountContactForm(el: HTMLElement): void {
  const form = el.querySelector("form") as HTMLFormElement;
  if (form) {
    new ContactForm(form);
    console.log("📧 ContactForm component mounted");
  } else {
    console.error("ContactForm: No form element found");
  }
}
