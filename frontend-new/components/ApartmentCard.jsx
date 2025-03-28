import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Card, CardContent, CardTitle, CardFooter } from './ui/card';
import { StarRating } from './ui';

/**
 * Форматирует цену в строку с валютой
 * @param {number} price - Цена для форматирования
 * @returns {string} Форматированная цена, например "₽1,500"
 */
const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(price);
};

/**
 * Компонент карточки квартиры
 * @param {Object} props - Свойства компонента
 * @param {Object} props.apartment - Данные о квартире
 * @returns {JSX.Element} Компонент карточки квартиры
 */
export default function ApartmentCard({ apartment }) {
  if (!apartment) {
    return null;
  }

  // Обработка ошибок загрузки изображений
  const handleImageError = (e) => {
    e.target.src = '/images/placeholder-apartment.jpg';
  };

  return (
    <Card className="overflow-hidden transition-shadow duration-300 hover:shadow-lg h-full flex flex-col">
      <div className="relative w-full h-48">
        <Image 
          src={apartment.image || '/images/placeholder-apartment.jpg'} 
          alt={apartment.title} 
          fill
          className="object-cover"
          onError={handleImageError}
        />
      </div>
      <CardContent className="p-4 flex-grow">
        <CardTitle className="text-xl mb-1 line-clamp-1">{apartment.title}</CardTitle>
        <p className="text-muted-foreground text-sm mb-3 line-clamp-1">{apartment.address}</p>
        <div className="flex justify-between items-center mb-2">
          <span className="font-bold text-lg">{formatPrice(apartment.price)}</span>
          <StarRating rating={apartment.rating} size="sm" />
        </div>
        <p className="text-sm text-muted-foreground line-clamp-2">{apartment.description}</p>
      </CardContent>
      <CardFooter className="px-4 pt-0 pb-4">
        <Link 
          href={`/apartment/${apartment.id}`}
          className="w-full inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Подробнее
        </Link>
      </CardFooter>
    </Card>
  );
}