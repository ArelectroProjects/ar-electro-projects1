import { motion } from 'framer-motion';

const EASE = [0.22, 1, 0.36, 1];

export function Reveal({ children, delay = 0, className = '', as = 'div', ...rest }) {
  const Tag = motion[as] || motion.div;
  return (
    <Tag
      className={className}
      initial={{ opacity: 0, y: 32 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.8, delay, ease: EASE }}
      {...rest}
    >
      {children}
    </Tag>
  );
}

export function MaskedLine({ children, delay = 0, className = '' }) {
  return (
    <span className={`mask-line ${className}`}>
      <motion.span
        className="mask-inner"
        initial={{ y: '112%' }}
        animate={{ y: '0%' }}
        transition={{ duration: 0.9, delay, ease: EASE }}
      >
        {children}
      </motion.span>
    </span>
  );
}

export function Marquee({ items }) {
  const row = items.map((t, i) => (
    <span key={i} className="marquee-item">
      {t} <i className="marquee-star">✕</i>
    </span>
  ));
  return (
    <div className="marquee" data-testid="editorial-marquee">
      <div className="marquee-track">
        {row}
        {row}
      </div>
    </div>
  );
}
