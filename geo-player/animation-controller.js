/**
 * Controlador de animaciones para deck.gl
 * Gestiona la reproducción secuencial de animaciones de capas, cámara e imágenes
 */

class AnimationController {
  constructor(config) {
    this.animations = config.animations || [];
    this.currentIndex = -1;
    this.isPlaying = false;
    this.isPaused = false;
    this.timeoutId = null;
    this.animationFrameId = null;
    this.progressIntervalId = null;

    // Callbacks
    this.onLayersChange = null;
    this.onCameraChange = null;
    this.onImageShow = null;
    this.onAnimationChange = null;
    this.onProgressUpdate = null;

    // Estado de transiciones
    this.transitionStart = null;
    this.transitionDuration = 0;
    this.cameraStart = null;
    this.cameraTarget = null;

    // Estado de progreso
    this.waitStart = null;
    this.waitDuration = 0;
  }

  /**
   * Inicia la reproducción automática desde el principio
   */
  play() {
    if (this.animations.length === 0) return;

    this.isPlaying = true;
    this.isPaused = false;

    if (this.currentIndex === -1 || this.currentIndex >= this.animations.length - 1) {
      this.currentIndex = 0;
    } else {
      this.currentIndex++;
    }

    this.executeAnimation(this.currentIndex);
  }

  /**
   * Pausa la reproducción
   */
  pause() {
    this.isPaused = true;
    this.isPlaying = false;

    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }

    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }

    if (this.progressIntervalId) {
      clearInterval(this.progressIntervalId);
      this.progressIntervalId = null;
    }
  }

  /**
   * Avanza a la siguiente animación
   */
  next() {
    const nextIndex = this.currentIndex + 1;
    if (nextIndex < this.animations.length) {
      this.goToAnimation(nextIndex);
    }
  }

  /**
   * Retrocede a la animación anterior
   */
  previous() {
    const prevIndex = this.currentIndex - 1;
    if (prevIndex >= 0) {
      this.goToAnimation(prevIndex);
    }
  }

  /**
   * Salta a una animación específica
   */
  goToAnimation(index) {
    if (index < 0 || index >= this.animations.length) return;

    // Limpiar timeouts previos
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }

    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }

    if (this.progressIntervalId) {
      clearInterval(this.progressIntervalId);
      this.progressIntervalId = null;
    }

    this.currentIndex = index;
    this.executeAnimation(index);

    // Si estaba reproduciéndose, continuar
    if (this.isPlaying && !this.isPaused) {
      this.scheduleNext();
    }
  }

  /**
   * Ejecuta una animación específica
   */
  executeAnimation(index) {
    if (index < 0 || index >= this.animations.length) return;

    const animation = this.animations[index];
    this.currentIndex = index;

    // Notificar cambio de animación
    if (this.onAnimationChange) {
      this.onAnimationChange(animation, index);
    }

    // Ejecutar según el tipo (o múltiples tipos simultáneamente)
    // Si tiene 'layers' y 'camera', ejecutar ambos
    if (animation.layers && animation.camera) {
      this.executeLayers(animation);
      this.executeCamera(animation);
    } else {
      // Comportamiento original basado en type
      switch (animation.type) {
        case 'layers':
          this.executeLayers(animation);
          break;
        case 'camera':
          this.executeCamera(animation);
          break;
        case 'image':
          this.executeImage(animation);
          break;
      }
    }

    // Programar siguiente animación si está en play
    if (this.isPlaying && !this.isPaused) {
      this.scheduleNext();
    }
  }

  /**
   * Ejecuta animación de capas
   */
  executeLayers(animation) {
    if (this.onLayersChange) {
      this.onLayersChange(animation.layers, animation.duration * 1000);
    }
  }

  /**
   * Ejecuta animación de cámara con interpolación suave
   */
  executeCamera(animation) {
    if (!this.onCameraChange) return;

    const duration = animation.duration * 1000;
    this.transitionStart = performance.now();
    this.transitionDuration = duration;
    this.cameraTarget = animation.camera;

    // Iniciar animación con requestAnimationFrame
    const animate = (currentTime) => {
      if (!this.transitionStart) return;

      const elapsed = currentTime - this.transitionStart;
      const progress = Math.min(elapsed / this.transitionDuration, 1);

      // Función de easing (ease-in-out)
      const eased = progress < 0.5
        ? 2 * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 2) / 2;

      if (this.onCameraChange) {
        this.onCameraChange(this.cameraTarget, eased);
      }

      if (progress < 1) {
        this.animationFrameId = requestAnimationFrame(animate);
      } else {
        this.transitionStart = null;
        this.animationFrameId = null;
      }
    };

    this.animationFrameId = requestAnimationFrame(animate);
  }

  /**
   * Ejecuta animación de imagen
   */
  executeImage(animation) {
    if (this.onImageShow) {
      this.onImageShow(animation.image, animation.duration * 1000);
    }
  }

  /**
   * Programa la siguiente animación
   */
  scheduleNext() {
    const nextIndex = this.currentIndex + 1;

    if (nextIndex >= this.animations.length) {
      // Fin de la secuencia
      this.isPlaying = false;
      if (this.progressIntervalId) {
        clearInterval(this.progressIntervalId);
        this.progressIntervalId = null;
      }
      return;
    }

    const currentAnimation = this.animations[this.currentIndex];
    const waitTime = (currentAnimation.waitTime || 0) * 1000; // waitTime individual en milisegundos
    const totalTime = (currentAnimation.duration * 1000) + waitTime;

    // Iniciar barra de progreso - ahora cubre duration + waitTime
    this.waitStart = performance.now();
    this.waitDuration = totalTime; // Cambio: ahora es el tiempo total

    // Actualizar progreso cada 50ms
    if (this.progressIntervalId) {
      clearInterval(this.progressIntervalId);
    }

    this.progressIntervalId = setInterval(() => {
      if (!this.waitStart || !this.isPlaying) return;

      const elapsed = performance.now() - this.waitStart;
      const progress = Math.min(elapsed / this.waitDuration, 1);
      const remaining = Math.max(0, (this.waitDuration - elapsed) / 1000);

      if (this.onProgressUpdate) {
        this.onProgressUpdate(progress, remaining);
      }

      if (progress >= 1) {
        clearInterval(this.progressIntervalId);
        this.progressIntervalId = null;
      }
    }, 50);

    this.timeoutId = setTimeout(() => {
      if (this.isPlaying && !this.isPaused) {
        if (this.progressIntervalId) {
          clearInterval(this.progressIntervalId);
          this.progressIntervalId = null;
        }
        this.currentIndex = nextIndex;
        this.executeAnimation(nextIndex);
      }
    }, totalTime);
  }

  /**
   * Obtiene la animación actual
   */
  getCurrentAnimation() {
    if (this.currentIndex < 0 || this.currentIndex >= this.animations.length) {
      return null;
    }
    return this.animations[this.currentIndex];
  }

  /**
   * Obtiene todas las animaciones
   */
  getAllAnimations() {
    return this.animations;
  }

  /**
   * Obtiene el índice actual
   */
  getCurrentIndex() {
    return this.currentIndex;
  }

  /**
   * Verifica si está reproduciendo
   */
  getIsPlaying() {
    return this.isPlaying;
  }

  /**
   * Verifica si está pausado
   */
  getIsPaused() {
    return this.isPaused;
  }
}
