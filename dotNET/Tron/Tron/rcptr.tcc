/*
 * Reference Counted Pointer Class
 * Copyright (C) J.A. du Preez
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 *
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 *
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 */

/*
  $Id: rcptr.tcc 96 2005-01-19 13:07:51Z bholt $
*/

template<class T>
inline RCPtr<T>::RCPtr() : oPtr(0) {
  cPtr = new unsigned;
  *cPtr = 1;
} // default constructor

template<class T>
inline RCPtr<T>::RCPtr(const RCPtr& rcp) : oPtr(rcp.oPtr), cPtr(rcp.cPtr) {
  (*cPtr)++;
} // copy constructor

template<class T>
template <class FromType>
inline RCPtr<T>::RCPtr(const RCPtr<FromType>& rcp) : oPtr( rcp.objPtr() ), cPtr( rcp.cntPtr() ) {
  (*cPtr)++;
} // constructor

template<class T>
inline RCPtr<T>::~RCPtr() {
  if ( !( --(*cPtr) ) ) {
    delete oPtr;
    oPtr = 0;
    delete cPtr;
    cPtr = 0;
  } // if
} // destructor

template<class T>
inline RCPtr<T>::RCPtr(T* justNewed) : oPtr(justNewed) {
  cPtr = new unsigned;
  *cPtr = 1;
} // constructor

template<class T>
inline RCPtr<T>::RCPtr(T* objectPtr, unsigned* countPtr) : oPtr(objectPtr), cPtr(countPtr) {
  (*cPtr)++;
} // constructor

template<class T>
inline RCPtr<T>& RCPtr<T>::operator=(const RCPtr& rhs) {
  return assignFrom( rhs.objPtr(), rhs.cntPtr() );
} // operator=

template<class T>
template <class FromType>
inline RCPtr<T>& RCPtr<T>::operator=(const RCPtr<FromType>& rhs) {
  return assignFrom( rhs.objPtr(), rhs.cntPtr() );
} // operator=
  
template<class T>
inline T* RCPtr<T>::operator->() const { 
  
  // adt // 
  // 05/04/2001 // 
  // 17:16 // 
  // Added a check for dereference of a null object pointer
    
#ifdef DEBUG_MODE
  if (!oPtr) {

    cerr << "ERROR => RCPtr::operator-> : Dereferencing null pointer\n"
         << __FILE__ << " line " << __LINE__ << endl;
    abort();
  } // if
#endif // DEBUG_MODE
    
  return oPtr; 
  
} // operator->

template<class T>
inline T& RCPtr<T>::operator*() const { 
    
  // adt //
  // 05/04/2001 //
  // 17:16 // 
  // Added a check for dereferencing a null object pointer
    
#ifdef DEBUG_MODE
  if (!oPtr) {
    
    cerr << "ERROR => RCPtr::operator* : Dereferencing null pointer\n"
         << __FILE__ << " line " << __LINE__ << endl;
    abort();
  } // if
#endif // DEBUG_MODE

  return *oPtr; 
 
} // operator*

template<class T>
inline RCPtr<T>::operator bool() const {
  return oPtr != 0;
} // operator bool
  
//=====================others======================================

template<class T>
inline T* RCPtr<T>::objPtr() const {
  return oPtr;
} // objPtr

template<class T>
inline unsigned* RCPtr<T>::cntPtr() const {
  return cPtr;
} // cntPtr

template<class T>
inline void RCPtr<T>::makeImmortal() {
  (*cPtr)++;
} // makeImmortal

template<class T>
inline bool RCPtr<T>::shared() const {
  return oPtr && *cPtr > 1;
} // shared

template<class T>
inline RCPtr<T>& RCPtr<T>::assignFrom(T* objectPtr, unsigned* countPtr) {
  (*cPtr)--;
  (*countPtr)++;
  if ( !(*cPtr) ) {
    delete cPtr; 
    delete oPtr;
  } // if
  cPtr = countPtr;
  oPtr = objectPtr;
  return *this;
} // assignFrom

//=====================friends=====================================

template<class ToType, class FromType>
RCPtr<ToType> dynamicCast(const RCPtr<FromType>& fromPtr) {
  ToType* rawPtr = dynamic_cast<ToType*>( fromPtr.objPtr() );
  if (rawPtr) {
    return RCPtr<ToType> ( rawPtr, fromPtr.cntPtr() );
  } // if
  else {
    return RCPtr<ToType>(0);
  } // else
} // dynamicCast

template<class ToType, class FromType>
RCPtr<ToType> constCast(const RCPtr<FromType>& fromPtr) {
  ToType* rawPtr = const_cast<ToType*>( fromPtr.objPtr() );
  return RCPtr<ToType> ( rawPtr, fromPtr.cntPtr() );
} // constCast

template<class ToType, class FromType>
bool assignTo(RCPtr<ToType>& toPtr, const RCPtr<FromType>& fromPtr) {
  ToType* rawPtr = dynamic_cast<ToType*>( fromPtr.objPtr() );
  if (rawPtr) {
    return toPtr.assignFrom( rawPtr, fromPtr.cntPtr() );
  } // if
  else {
    return toPtr = RCPtr<ToType>(0);
  } // else
} // assignTo
     
template<class T>
inline ostream& operator<<(ostream& file, const RCPtr<T>& rcp ) {
  return file << (*rcp.cPtr) << " refs to " << rcp. oPtr;
} // operator<<
  

/*
  $Log: rcptr.tcc,v $
  Revision 1.1  2004/09/13 14:02:06  jcronje
  Moved header files into the includes/sdr directory

  Revision 1.5  2003/11/19 12:53:00  jcronje
  This class in now licensed under the LGPL

  Revision 1.2  2002/09/26 16:24:42  edward
  cosmetic [EdV]

  Revision 1.1  2002/05/31 14:23:09  dupreez
  Moved code out of .hpp files [EdV]

*/
